import re
import scrapy
import logging
from manga_scraper.utils.pdf_converter import convert_chapter_to_pdf
from manga_scraper.utils.progress_bar import ProgressBar
from scrapy_playwright.page import PageMethod
from manga_scraper.utils.paginator import ChapterPaginator
from manga_scraper.utils.chapter_sorter import ChapterSorter
from manga_scraper.utils.chapter_index import ChapterIndexResolver
from manga_scraper.utils.download_manager import download_and_save_image
from manga_scraper.utils.chapter_downloader import prepare_chapter_download
from manga_scraper.utils.chapter_requester import request_next_chapter
from manga_scraper.utils.chapter_display import print_chapter_summary

# Suppress default Scrapy logging output to reduce verbosity
logging.getLogger('scrapy').setLevel(logging.WARNING)

class BaseMangaSpider(scrapy.Spider):
    # Core spider metadata
    name = "base_manga_spider"
    site_name = "site_name"
    allowed_domains = ["example.com"]

    # Configuration for chapter extraction
    chapter_list = [""]
    chapter_map = {}
    chapter_list_selector = 'a.chapter-link::attr(href)'  # CSS selector for chapter URLs
    chapter_pattern = r'chapter-(\d+)'  # Regex pattern to extract chapter number
    start_chapter = 0  # Starting chapter number
    paginate = False  # Flag indicating whether pagination is used
    url_template = "https://example.com/manga/chapter-{chapter}/"  # URL format string for chapter pages
    start_url = "https://example.com"

    anti_scraping_url = False

    # Image-related configuration
    image_selector = "img.page-image"  # CSS selector for image elements
    file_ext = ".jpg"  # Default image file extension
    root_dir = "downloads"  # Root directory for storing downloaded content

    # Pagination-related state variables
    page = 1
    all_chapters = []
    has_more_pages = True

    # Download progress bar instance
    progress_bar = ProgressBar()

    use_playwright = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_progress_length = 0

        # Instantiate the paginator for chapter list pagination
        self.paginator = ChapterPaginator(
            start_url=self.start_url,
            selector=self.chapter_list_selector,
            pattern=self.chapter_pattern
        )

    def start_requests(self):
        """Trigger the initial request to the starting URL to begin scraping"""
        print(f"\n🚀 Starting download for site: {self.site_name}\n")
        yield scrapy.Request(url=self.start_url, callback=self.parse_chapter_list)

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

        if self.anti_scraping_url:
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
            self.chapter_index = ChapterIndexResolver.resolve_index(self.chapter_map, self.start_chapter)
        else: 
            self.chapter_list = ChapterSorter.sort_and_deduplicate(raw_chapters)
            print_chapter_summary(self.chapter_list)
            self.chapter_index = ChapterIndexResolver.resolve_index(self.chapter_list, self.start_chapter)

        print(f"📍 Starting download from chapter {self.start_chapter} at index {self.chapter_index}")

        if self.chapter_list or self.chapter_map:
            if self.chapter_map:
                chapter_map_key = list(self.chapter_map.keys())[self.chapter_index] 
                chapter_map_val=list(self.chapter_map.values())[self.chapter_index]
            else:
                chapter_list_val = self.chapter_list[self.chapter_index]

            if self.use_playwright:
                result = prepare_chapter_download(self.root_dir, self.site_name, chapter_map_key, use_playwright=self.use_playwright)
                skip = result[0]
                if skip:
                    for req in request_next_chapter(self, self.chapter_map):
                        yield req

            chapter = chapter_map_val if self.chapter_map else chapter_list_val
            chapter_url = self.url_template.format(chapter=chapter)
            meta = {
                'chapter': chapter_map_key if  self.chapter_map else chapter_list_val
            }
            if self.use_playwright:
                meta.update({
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", self.image_selector),
                        PageMethod("wait_for_timeout", 1000),
                    ],
                    "playwright_page_goto_kwargs": {"wait_until": "domcontentloaded"},
                    "playwright_include_page": True,
                })
            yield scrapy.Request(
                url=chapter_url,
                callback=self.parse_chapter,
                meta=meta,
                errback=self.handle_error
            )

        else:
            print("⚠️ No chapters found")

    async def parse_chapter(self, response):
        """Parse a chapter page and initiate download of all images within the chapter"""
        chapter = response.meta['chapter']

        if "playwright_page" in response.meta:
            page = response.meta["playwright_page"]
            await page.wait_for_selector(self.image_selector)
            img_elements = await page.query_selector_all(self.image_selector)
            img_urls = [await el.get_attribute("src") for el in img_elements]
        else:
            img_urls = response.css(f"{self.image_selector}::attr(src)").getall()

        # Determine whether to skip the chapter and prepare relevant metadata
        skip, folder, meta = prepare_chapter_download(
            root_dir=self.root_dir,
            site_name=self.site_name,
            chapter=chapter,
            img_urls=img_urls,
            file_ext=self.file_ext,
            progress_bar=self.progress_bar,
        )

        if skip:
            # Skip this chapter and proceed to the next one
            for req in request_next_chapter(self, chapter_list_or_map=self.chapter_map if self.anti_scraping_url else  self.chapter_list):
                yield req
            return
        
        if "playwright_page" in response.meta:
            for index, img_url in enumerate(img_urls):
                    if await download_and_save_image(page, img_url, index, folder, self.file_ext,self.use_playwright):
                        progress_text = f"⏳ Chapter {chapter}: {self.progress_bar.progress_bar(index + 1, len(img_urls))} ({index + 1}/{len(img_urls)}) "
                        self.progress_bar.update_progress(progress_text)
                    else:
                        for req in request_next_chapter(self,  self.chapter_map):
                            yield req
                        return
            # Once all images are downloaded, convert the folder to PDF
            self.progress_bar.clear_progress()
            logging.info(f"✅ Chapter {chapter}: Download completed!")
            convert_chapter_to_pdf(folder)
            for req in request_next_chapter(self, self.chapter_map):
                yield req
        else:
            # Start downloading the first image of the chapter
            yield scrapy.Request(
                url=img_urls[0],
                callback=self.download_image,
                errback=self.handle_error,
                meta=meta,
                dont_filter=True
            )

    def download_image(self, response):
        """Download a single image and continue downloading remaining images recursively"""
        chapter = response.meta['chapter']
        img_urls = response.meta['img_urls']
        index = response.meta['index']
        folder = response.meta['folder']
        total = response.meta['total']
        downloaded = response.meta['downloaded'] + 1

        if not download_and_save_image(response, img_urls, index, folder, self.file_ext, self.use_playwright):
            # If download fails, proceed to the next chapter
            yield from request_next_chapter(self, chapter_list_or_map=self.chapter_list) 
            return

        # Update the download progress bar in the terminal
        progress_text = f"⏳ Chapter {chapter}: {self.progress_bar.progress_bar(downloaded, total)} ({downloaded}/{total}) "
        self.progress_bar.update_progress(progress_text)

        if index + 1 < total:
                # Continue downloading the next image
                yield scrapy.Request(
                    url=img_urls[index + 1],
                    callback=self.download_image,
                    errback=self.handle_error,
                    meta={
                        'chapter': chapter,
                        'img_urls': img_urls,
                        'index': index + 1,
                        'folder': folder,
                        'total': total,
                        'downloaded': downloaded
                    },
                    dont_filter=True
                )
        else:
            # Once all images are downloaded, convert the folder to PDF
            self.progress_bar.clear_progress()
            logging.info(f"✅ Chapter {chapter}: Download completed!")
            convert_chapter_to_pdf(folder)
            yield from request_next_chapter(self, chapter_list_or_map=self.chapter_list)

    def handle_error(self, failure):
        """Handle exceptions or request failures gracefully and move to the next chapter"""
        chapter = failure.request.meta['chapter']
        logging.error(f"❌ Error occurred while downloading chapter {chapter}: {failure.value}\n")
        yield from request_next_chapter(self, chapter_list_or_map=self.chapter_map if self.anti_scraping_url else  self.chapter_list)
