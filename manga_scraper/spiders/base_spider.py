import scrapy
import logging
from manga_scraper.utils.pdf_converter import convert_chapter_to_pdf
from manga_scraper.utils.progress_bar import ProgressBar
from manga_scraper.utils.paginator import ChapterPaginator
from manga_scraper.utils.chapter_sorter import ChapterSorter
from manga_scraper.utils.chapter_index import ChapterIndexResolver
from manga_scraper.utils.download_manager import download_and_save_image
from manga_scraper.utils.chapter_downloader import prepare_chapter_download
from manga_scraper.utils.chapter_requester import request_next_chapter
from manga_scraper.utils.chapter_display import print_chapter_summary

# TODO: For chapters that cannot be merged into a complete volume, append a suffix "-xxx" to the directory name.
#       Example: chapter-96-xxx, chapter-95-xxx

# Suppress default Scrapy logging output to reduce verbosity
logging.getLogger('scrapy').setLevel(logging.WARNING)

class BaseMangaSpider(scrapy.Spider):
    # Core spider metadata
    name = "base_manga_spider"
    site_name = "site_name"
    allowed_domains = ["example.com"]

    # Configuration for chapter extraction
    chapter_list = [""]
    chapter_list_selector = 'a.chapter-link::attr(href)'  # CSS selector for chapter URLs
    chapter_pattern = r'chapter-(\d+)'  # Regex pattern to extract chapter number
    start_chapter = 0  # Starting chapter number
    paginate = False  # Flag indicating whether pagination is used
    url_template = "https://example.com/manga/chapter-{chapter}/"  # URL format string for chapter pages
    start_url = "https://example.com"

    # Image-related configuration
    image_selector = "img.page-image"  # CSS selector for image elements
    image_attr = "src"  # Attribute containing the image URL
    file_ext = ".jpg"  # Default image file extension
    root_dir = "downloads"  # Root directory for storing downloaded content

    # Pagination-related state variables
    page = 1
    all_chapters = []
    has_more_pages = True

    # Download progress bar instance
    progress_bar = ProgressBar()

    # Custom spider-specific Scrapy settings
    custom_settings = {
        'LOG_LEVEL': 'ERROR',
        'TELNETCONSOLE_ENABLED': False
    }

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

        # Remove duplicates and sort chapter identifiers
        self.chapter_list = ChapterSorter.sort_and_deduplicate(raw_chapters)

        # Print a summary of unique chapters without flooding the console
        print_chapter_summary(self.chapter_list)

        # Determine the index from which to start downloading
        self.chapter_index = ChapterIndexResolver.resolve_index(self.chapter_list, self.start_chapter)
        print(f"📍 Starting download from chapter {self.start_chapter} at index {self.chapter_index}")
        
        if self.chapter_list:
            # Initiate download for the first chapter in the resolved list
            yield scrapy.Request(
                url=self.url_template.format(chapter=self.chapter_list[self.chapter_index]),
                callback=self.parse_chapter,
                meta={'chapter': self.chapter_list[self.chapter_index]},
                errback=self.handle_error
            )
        else:
            print("⚠️ No chapters found")

    def parse_chapter(self, response):
        """Parse a chapter page and initiate download of all images within the chapter"""
        chapter = response.meta['chapter']
        img_urls = response.css(f"{self.image_selector}::attr({self.image_attr})").getall()

        # Determine whether to skip the chapter and prepare relevant metadata
        skip, folder, meta = prepare_chapter_download(
            root_dir=self.root_dir,
            site_name=self.site_name,
            chapter=chapter,
            img_urls=img_urls,
            file_ext=self.file_ext,
            progress_bar=self.progress_bar
        )

        if skip:
            # Skip this chapter and proceed to the next one
            yield from request_next_chapter(self)
            return

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

        if not download_and_save_image(response, img_urls, index, folder, self.file_ext):
            # If download fails, proceed to the next chapter
            yield from request_next_chapter(self)
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
            yield from request_next_chapter(self)

    def handle_error(self, failure):
        """Handle exceptions or request failures gracefully and move to the next chapter"""
        chapter = failure.request.meta['chapter']
        logging.error(f"❌ Error occurred while downloading chapter {chapter}: {failure.value}\n")
        yield from request_next_chapter(self)
