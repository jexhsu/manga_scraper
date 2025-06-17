import re
import scrapy
import logging
from manga_scraper.utils.pdf_converter import convert_chapter_to_pdf
from manga_scraper.utils.progress_bar import ProgressBar
from manga_scraper.utils.paginator import ChapterPaginator
from manga_scraper.utils.chapter_downloader import prepare_chapter_download
from manga_scraper.utils.chapter_requester import request_next_chapter
from manga_scraper.utils.chapter_display import print_chapter_summary
from manga_scraper.utils.retry import async_retry_chapter_download, sync_retry_chapter_download
from manga_scraper.utils.chapter_checker import check_chapter_completion_and_get_start_index
from manga_scraper.utils.error_handling import retry_on_failure
from manga_scraper.utils.chapter_url_processor import process_chapter_urls
from manga_scraper.utils.chapter_list_parser import parse_chapter_list
from manga_scraper.utils.image_url_extractor import extract_image_urls
from manga_scraper.utils.url_processor import process_chapter_url
from manga_scraper.utils.chapter_progress import check_and_log_chapter_progress
from manga_scraper.utils.playwright_setup import setup_playwright_meta
from manga_scraper.utils.error_handler import handle_spider_error

# Suppress default Scrapy logging output to reduce verbosity
logging.getLogger('scrapy').setLevel(logging.WARNING)

class BaseMangaSpider(scrapy.Spider):
    name = "base_manga_spider"
    site_name = "site_name"
    allowed_domains = ["example.com"]

    chapter_list = [""]
    chapter_map = {}
    chapter_completed_map = {}
    chapter_list_selector = 'a.chapter-link::attr(href)'
    chapter_pattern = r'chapter-(\d+)'
    paginate = False
    url_template = "https://example.com/manga/chapter-{chapter}/"
    start_url = "https://example.com"

    anti_scraping_url = False

    image_selector = "img.page-image"
    root_dir = "downloads"

    page = 1
    all_chapters = []
    has_more_pages = True

    progress_bar = ProgressBar()
    use_playwright = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_progress_length = 0
        self.paginator = ChapterPaginator(
            start_url=self.start_url,
            selector=self.chapter_list_selector,
            pattern=self.chapter_pattern
        )
    @retry_on_failure(max_retries=3)
    def start_requests(self):
        print(f"\n🚀 Starting download for site: {self.site_name}\n")
        yield scrapy.Request(url=self.start_url, callback=self.parse_chapter_list, errback=self.handle_error)

    def parse_chapter_list(self, response):
        """
        Parse the chapter list from the response, handling pagination and determining 
        where to start downloading based on completed chapters.
        
        Args:
            response (scrapy.http.Response): The response object from Scrapy.
        """
        # Delegate parsing logic to utility function
        chapter_map, chapter_list, chapter_index, next_page = parse_chapter_list(response, self)
        
        # Handle pagination
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse_chapter_list)
            return
        
        # Update spider state with parsed data
        self.chapter_map, self.chapter_list, self.chapter_index = chapter_map, chapter_list, chapter_index

        # Extract progress logging to utility
        should_continue = check_and_log_chapter_progress(self.chapter_index, self.chapter_list, self.chapter_map)
        if not should_continue:
            return

        # Extract chapter URL processing logic to utils
        chapter_url, meta = process_chapter_url(self, self.chapter_map, self.chapter_list, self.chapter_index)

        if self.use_playwright:
            result = prepare_chapter_download(self.root_dir, self.site_name, meta['chapter'], use_playwright=True)
            skip = result[0]
            if skip:
                for req in request_next_chapter(self, self.chapter_map):
                    yield req

        if self.use_playwright:
           meta = setup_playwright_meta(meta, self.image_selector)
            
        yield scrapy.Request(
            url=chapter_url,
            callback=self.parse_chapter,
            meta=meta,
            errback=self.handle_error
        )

    async def parse_chapter(self, response):
        try:
            
            chapter = response.meta['chapter']

            img_urls = await extract_image_urls(response, self)

            skip, folder, meta = prepare_chapter_download(
                root_dir=self.root_dir,
                site_name=self.site_name,
                chapter=chapter,
                img_urls=img_urls,
                progress_bar=self.progress_bar,
            )

            if skip:
                for req in request_next_chapter(self, self.chapter_map if self.chapter_map else self.chapter_list):
                    yield req
                return

            if "playwright_page" in response.meta:
                # Call retry-enabled async chapter downloader
                async for req in async_retry_chapter_download(self, response, img_urls, chapter, folder, meta):
                    yield req
                return
            else:
                yield scrapy.Request(
                    url=img_urls[0],
                    callback=self.download_image,
                    errback=self.handle_error,
                    meta=meta,
                    dont_filter=True
                )

        except Exception as e:
            await handle_spider_error(self, response, e)
            raise IgnoreRequest from e  # Skip this chapter but continue with others

    def download_image(self, response):
        chapter = response.meta['chapter']
        img_urls = response.meta['img_urls']
        index = response.meta['index']
        folder = response.meta['folder']
        total = response.meta['total']
        downloaded = response.meta['downloaded'] + 1
        
        yield from sync_retry_chapter_download(self, response)


    def handle_error(self, failure):
        # Replace with utility call
        yield from handle_spider_error(self, failure.request, failure.value)