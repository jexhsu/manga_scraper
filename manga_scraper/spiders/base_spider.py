import re
import time
import scrapy
import logging
from manga_scraper.utils.pdf_converter import convert_chapter_to_pdf
from manga_scraper.utils.print_chapter_status_grid import print_chapter_completion_map
from manga_scraper.utils.progress_bar import ProgressBar
from manga_scraper.utils.paginator import ChapterPaginator
from manga_scraper.utils.chapter_downloader import prepare_chapter_download
from manga_scraper.utils.chapter_requester import request_next_chapter
from manga_scraper.utils.chapter_display import print_chapter_summary
from manga_scraper.utils.chapter_checker import check_chapter_completion_and_get_start_index
from manga_scraper.utils.image_url_extractor import extract_image_urls
from manga_scraper.utils.download_manager import download_and_save_image
from manga_scraper.utils.playwright_setup import setup_playwright_meta
from scrapy.utils.response import response_status_message

# Suppress default Scrapy logging output to reduce verbosity
logging.getLogger('scrapy').setLevel(logging.WARNING)

class BaseMangaSpider(scrapy.Spider):
    name = "base_manga_spider"
    site_name = "site_name"
    allowed_domains = ["example.com"]

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

    max_retries = 5  # Maximum retry attempts for a chapter
    current_retry = 0  # Current retry count for the ongoing chapter

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
        """Extract the full list of chapters from the manga main page"""
        if self.paginate:
            # If pagination is enabled, recursively fetch all pages
            self.paginator.extract_chapters(response)
            if self.paginator.has_more_pages:
                next_page = self.paginator.next_page_url()
                yield scrapy.Request(url=next_page, callback=self.parse_chapter_list)
                return
            raw_chapters = self.paginator.all_chapters
        else:
            # Directly extract chapter identifiers without pagination
            raw_chapters = response.css(self.chapter_list_selector).re(self.chapter_pattern)
            
        # Processing raw_chapters into a dictionary with formatted keys
        descending_chapter_map = {}
        pattern = re.compile(r'(?:ch|chapter)-0*(\d+(?:-\d+)*)', re.IGNORECASE)

        for raw in raw_chapters:
            match = pattern.search(raw)
            if match:
                chapter_key = f"{match.group(1)}"
            else:
                chapter_key = raw  
            descending_chapter_map[chapter_key] = raw
        
        ascending_chapter_map = {k: v for k, v in sorted(descending_chapter_map.items(), key=lambda item: int(re.search(r'\d+', item[0]).group()))}

        self.chapter_map = ascending_chapter_map

        print_chapter_summary(self.chapter_map)

        self.chapter_index = check_chapter_completion_and_get_start_index(
            self.root_dir,
            self.site_name,
            self.chapter_map,
            self
        )

        print_chapter_completion_map(self.chapter_completed_map)

        start_chapter = list(self.chapter_map.keys())[self.chapter_index]

        print(f"\n📍 Starting download from chapter {start_chapter}")

        # breakpoint()

        if self.chapter_index >= len(self.chapter_map):
            print("🎉 All chapters already completed. Nothing to download.")
            return
        
        if self.chapter_map:
            chapter_map_key = list(self.chapter_map.keys())[self.chapter_index] 
            chapter_map_val=list(self.chapter_map.values())[self.chapter_index]
            if self.use_playwright:
                result = prepare_chapter_download(self.root_dir, self.site_name, chapter_map_key, use_playwright=self.use_playwright)
                skip = result[0]
                if skip:
                    for req in request_next_chapter(self, self.chapter_map):
                        yield req

            chapter_url = self.url_template.format(chapter=chapter_map_val)

            meta = {
                'chapter': chapter_map_key
            }
            
            if self.use_playwright:
                meta = setup_playwright_meta(meta, self.image_selector)
            yield scrapy.Request(
                url=chapter_url,
                callback=self.parse_chapter,
                meta=meta,
                errback=self.handle_error_with_retry
            )

        else:
            print("⚠️ No chapters found")

    async def parse_chapter(self, response):
        chapter = response.meta['chapter']

        page, img_urls = await extract_image_urls(response, self)

        skip, folder, meta = prepare_chapter_download(
            root_dir=self.root_dir,
            site_name=self.site_name,
            chapter=chapter,
            img_urls=img_urls,
            progress_bar=self.progress_bar,
        )

        if skip:
            # Skip this chapter and proceed to the next one
            for req in request_next_chapter(self, self.chapter_map):
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
            yield from request_next_chapter(self, self.chapter_map) 
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
            yield from request_next_chapter(self, self.chapter_map)


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
        yield from request_next_chapter(self, self.chapter_map)