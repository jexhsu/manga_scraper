import re
import scrapy
import logging
from manga_scraper.utils.pdf_converter import convert_chapter_to_pdf
from manga_scraper.utils.progress_bar import ProgressBar
from manga_scraper.utils.paginator import ChapterPaginator
from manga_scraper.utils.chapter_downloader import prepare_chapter_download
from manga_scraper.utils.chapter_requester import request_next_chapter
from manga_scraper.utils.chapter_display import print_chapter_summary
from manga_scraper.utils.chapter_checker import check_chapter_completion_and_get_start_index
from manga_scraper.utils.chapter_url_processor import process_chapter_urls
from manga_scraper.utils.chapter_list_parser import parse_chapter_list
from manga_scraper.utils.image_url_extractor import extract_image_urls
from manga_scraper.utils.url_processor import process_chapter_url
from manga_scraper.utils.chapter_progress import check_and_log_chapter_progress
from manga_scraper.utils.download_manager import download_and_save_image
from manga_scraper.utils.playwright_setup import setup_playwright_meta

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
            # Skip this chapter and proceed to the next one
            for req in request_next_chapter(self, self.chapter_map if self.chapter_map else self.chapter_list):
                yield req
            return

        if "playwright_page" in response.meta:
            start_index = meta.get("index", 0) or 0
            for index in range(start_index, len(img_urls)):
                    img_url = img_urls[index]
                    if await download_and_save_image(page, img_url, index, folder, self.use_playwright):
                        progress_text = f"⏳ Chapter {chapter}: {self.progress_bar.progress_bar(index + 1, len(img_urls))} ({index + 1}/{len(img_urls)}) "
                        self.progress_bar.update_progress(progress_text)
                    else:
                        for req in request_next_chapter(self,  self.chapter_map):
                            yield req
                        return
            # Once all images are downloaded, convert the folder to PDF
            self.progress_bar.clear_progress()
            logging.info(f"✅ Chapter {chapter}: Download completed!")
            self.chapter_completed_map[chapter] = True
            convert_chapter_to_pdf(folder)
            for req in request_next_chapter(self, self.chapter_map):
                yield req
        else:
            # Start downloading the first image of the chapter
            yield scrapy.Request(
                url=img_urls[0],
                callback=self.download_image,
                errback=self.handle_error_with_retry,
                meta=meta,
                dont_filter=True
            )

    def download_image(self, response):
        chapter = response.meta['chapter']
        img_urls = response.meta['img_urls']
        index = response.meta['index']
        folder = response.meta['folder']
        total = response.meta['total']
        downloaded = response.meta['downloaded'] + 1
        
        if not download_and_save_image(response, img_urls, index, folder, self.use_playwright):
            # If download fails, proceed to the next chapter
            yield from request_next_chapter(self, self.chapter_list) 
            return

        # Update the download progress bar in the terminal
        progress_text = f"⏳ Chapter {chapter}: {self.progress_bar.progress_bar(downloaded, total)} ({downloaded}/{total}) "
        self.progress_bar.update_progress(progress_text)

        if index + 1 < total:
                # Continue downloading the next image
                yield scrapy.Request(
                    url=img_urls[index + 1],
                    callback=self.download_image,
                    errback=self.handle_error_with_retry,
                    meta={
                        'chapter': chapter,
                        'img_urls': img_urls,
                        'index': index + 1,
                        'folder': folder,
                        'total': total,
                        'downloaded': downloaded,
                        'retry_times': response.meta.get('retry_times', 0)
                    },
                    dont_filter=True
                )
        else:
            # Once all images are downloaded, convert the folder to PDF
            self.progress_bar.clear_progress()
            logging.info(f"✅ Chapter {chapter}: Download completed!")
            self.chapter_completed_map[chapter] = True
            convert_chapter_to_pdf(folder)
            yield from request_next_chapter(self, self.chapter_list)


    def handle_error_with_retry(self, failure):
        request = failure.request
        retry_times = request.meta.get('retry_times', 0)
        max_retry_times = self.settings.getint('RETRY_TIMES')
        
        if retry_times < max_retry_times:
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retry_times + 1
            retryreq.dont_filter = True
            
            reason = response_status_message(failure.value.response.status) if hasattr(failure.value, 'response') else str(failure.value)
            self.logger.warning(f'Retrying {request.url} (failed {retry_times + 1} times): {reason}')
            
            time.sleep(self.settings.getfloat('DOWNLOAD_RETRY_DELAY'))
            return retryreq
        else:
            return self.handle_error(failure)

    def handle_error(self, failure):
        chapter = failure.request.meta.get('chapter', 'unknown')
        logging.error(f"❌ Error occurred while downloading chapter {chapter}: {failure.value}\n")
        yield from request_next_chapter(self, self.chapter_map if self.chapter_map else self.chapter_list)