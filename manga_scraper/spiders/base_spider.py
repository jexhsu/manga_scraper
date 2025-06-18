# manga_scraper/spiders/base_spider.py
import os
import scrapy
import logging
from manga_scraper.utils.chapter_cleaner import clean_completed_chapters
from manga_scraper.utils.chapter_map import create_chapter_map
from manga_scraper.utils.chapter_resume import get_start_index
from manga_scraper.utils.pdf_converter import convert_chapter_to_pdf
from manga_scraper.utils.pdf_utils import get_pdf_output_path
from manga_scraper.utils.print_chapter_status_grid import print_chapter_completion_map
from manga_scraper.utils.progress_bar import ProgressBar
from manga_scraper.utils.paginator import ChapterPaginator
from manga_scraper.utils.chapter_downloader import prepare_chapter_download
from manga_scraper.utils.chapter_requester import request_next_chapter
from manga_scraper.utils.chapter_display import print_chapter_summary
from manga_scraper.utils.chapter_checker import (
    check_chapter_completion,
)
from manga_scraper.utils.image_url_extractor import extract_image_urls
from manga_scraper.utils.download_manager import download_and_save_image
from manga_scraper.utils.playwright_setup import setup_playwright_meta
from manga_scraper.utils.raw_chapter_extractor import extract_raw_chapters


class BaseMangaSpider(scrapy.Spider):
    name = "base_manga_spider"
    site_name = "site_name"
    allowed_domains = ["example.com"]

    chapter_map = {}
    chapter_completed_map = {}
    chapter_list_selector = "a.chapter-link::attr(href)"
    chapter_pattern = r"chapter-(\d+)"
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

    max_retries = 10  # Maximum retry attempts for a chapter
    current_retry = 0  # Current retry count for the ongoing chapter

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_progress_length = 0
        self.check_only = kwargs.get("check_only", False)
        self.paginator = ChapterPaginator(
            start_url=self.start_url,
            selector=self.chapter_list_selector,
            pattern=self.chapter_pattern,
        )
        logging.debug("BaseMangaSpider initialized with kwargs: %s", kwargs)

    def start_requests(self):
        print(f"\n🚀 Starting download for site: {self.site_name}\n")
        logging.debug("Starting initial request to: %s", self.start_url)
        yield scrapy.Request(
            url=self.start_url,
            callback=self.parse_chapter_list,
        )

    def parse_chapter_list(self, response):
        """Extract the full list of chapters from the manga main page"""
        logging.debug("Processing chapter list from URL: %s", response.url)

        # Use the utility function to extract raw chapters
        raw_chapters = extract_raw_chapters(
            response=response,
            paginate=self.paginate,
            paginator=self.paginator if self.paginate else None,
            chapter_list_selector=(
                self.chapter_list_selector if not self.paginate else None
            ),
            chapter_pattern=self.chapter_pattern if not self.paginate else None,
        )

        # Handle pagination continuation
        if self.paginate and self.paginator.has_more_pages:
            next_page = self.paginator.next_page_url()
            logging.debug("Yielding request for next page: %s", next_page)
            yield scrapy.Request(url=next_page, callback=self.parse_chapter_list)
            return

        # Use the utility function to create the chapter map
        self.chapter_map = create_chapter_map(raw_chapters)
        logging.debug("Processed chapter map: %s", self.chapter_map)

        self.chapter_completed_map = check_chapter_completion(
            self.root_dir, self.site_name, self.chapter_map
        )

        # New check-only mode - exit after printing status
        if self.check_only:
            import json

            print("COMPLETION_DATA:" + json.dumps(self.chapter_completed_map))
            return

        clean_completed_chapters(
            self.root_dir, self.site_name, self.chapter_completed_map
        )

        self.chapter_index = get_start_index(self.chapter_completed_map)

        logging.debug("Chapter index to start from: %s", self.chapter_index)

        print_chapter_summary(self.chapter_map, self.chapter_completed_map)

        print_chapter_completion_map(self.chapter_completed_map)

        if self.chapter_index >= len(self.chapter_map):
            logging.debug("All chapters already completed")
            print("\n🎉 All chapters already completed. Nothing to download.")
            return

        start_chapter = list(self.chapter_map.keys())[self.chapter_index]

        logging.debug("Starting download from chapter: %s", start_chapter)

        print(f"\n📍 Starting download from chapter {start_chapter}")

        if self.chapter_map:
            chapter_map_key = list(self.chapter_map.keys())[self.chapter_index]
            chapter_map_val = list(self.chapter_map.values())[self.chapter_index]
            if self.use_playwright:
                result = prepare_chapter_download(
                    self.root_dir,
                    self.site_name,
                    chapter_map_key,
                    use_playwright=self.use_playwright,
                )
                skip = result[0]
                if skip:
                    logging.debug(
                        "Skipping chapter %s (already exists)", chapter_map_key
                    )
                    for req in request_next_chapter(self, self.chapter_map):
                        yield req

            chapter_url = self.url_template.format(chapter=chapter_map_val)
            logging.debug("Chapter URL constructed: %s", chapter_url)

            meta = {"chapter": chapter_map_key}

            if self.use_playwright:
                meta = setup_playwright_meta(meta, self.image_selector)
                logging.debug("Playwright meta setup: %s", meta)
            logging.debug("Yielding request for chapter: %s", chapter_map_key)
            yield scrapy.Request(
                url=chapter_url,
                callback=self.parse_chapter,
                meta=meta,
            )

        else:
            logging.debug("No chapters found in chapter map")
            print("⚠️ No chapters found")

    async def parse_chapter(self, response):
        chapter = response.meta["chapter"]
        logging.debug("Processing chapter: %s from URL: %s", chapter, response.url)

        page, img_urls = await extract_image_urls(response, self)
        logging.debug("Extracted %d image URLs for chapter %s", len(img_urls), chapter)

        skip, folder, meta = prepare_chapter_download(
            root_dir=self.root_dir,
            site_name=self.site_name,
            chapter=chapter,
            img_urls=img_urls,
            progress_bar=self.progress_bar,
        )

        if skip:
            logging.debug("Skipping chapter %s (already exists)", chapter)
            # Skip this chapter and proceed to the next one
            for req in request_next_chapter(self, self.chapter_map):
                yield req
            return

        if "playwright_page" in response.meta:
            start_index = meta.get("index", 0) or 0
            logging.debug("Starting image downloads from index %d", start_index)
            for index in range(start_index, len(img_urls)):
                img_url = img_urls[index]
                if await download_and_save_image(
                    page, img_url, index, folder, self.use_playwright
                ):
                    progress_text = f"⏳ Chapter {chapter}: {self.progress_bar.progress_bar(index + 1, len(img_urls))} ({index + 1}/{len(img_urls)}) "
                    self.progress_bar.update_progress(progress_text)
                else:
                    logging.debug(
                        "Image download failed for chapter %s, index %d", chapter, index
                    )
                    for req in request_next_chapter(self, self.chapter_map):
                        yield req
                    return
            # Once all images are downloaded, convert the folder to PDF
            self.progress_bar.clear_progress()
            logging.info(f"✅ Chapter {chapter}: Download completed!")
            logging.debug("Converting chapter %s to PDF", chapter)
            convert_chapter_to_pdf(folder)
            self.chapter_completed_map[chapter] = os.path.exists(
                get_pdf_output_path(folder)
            )
            for req in request_next_chapter(self, self.chapter_map):
                yield req
        else:
            # Start downloading the first image of the chapter
            logging.debug("Starting non-playwright download for chapter %s", chapter)
            yield scrapy.Request(
                url=img_urls[0],
                callback=self.download_image,
                meta=meta,
                dont_filter=True,
            )

    def download_image(self, response):
        chapter = response.meta["chapter"]
        img_urls = response.meta["img_urls"]
        index = response.meta["index"]
        folder = response.meta["folder"]
        total = response.meta["total"]
        downloaded = response.meta["downloaded"] + 1
        logging.debug(
            "Downloading image %d/%d for chapter %s", index + 1, total, chapter
        )

        if not download_and_save_image(
            response, img_urls, index, folder, self.use_playwright
        ):
            logging.debug(
                "Image download failed for chapter %s, index %d", chapter, index
            )
            # If download fails, proceed to the next chapter
            yield from request_next_chapter(self, self.chapter_map)
            return

        # Update the download progress bar in the terminal
        progress_text = f"⏳ Chapter {chapter}: {self.progress_bar.progress_bar(downloaded, total)} ({downloaded}/{total}) "
        self.progress_bar.update_progress(progress_text)

        if index + 1 < total:
            # Continue downloading the next image
            logging.debug("Yielding request for next image in chapter %s", chapter)
            yield scrapy.Request(
                url=img_urls[index + 1],
                callback=self.download_image,
                meta={
                    "chapter": chapter,
                    "img_urls": img_urls,
                    "index": index + 1,
                    "folder": folder,
                    "total": total,
                    "downloaded": downloaded,
                    "retry_times": response.meta.get("retry_times", 0),
                },
                dont_filter=True,
            )
        else:
            # Once all images are downloaded, convert the folder to PDF
            self.progress_bar.clear_progress()
            logging.info(f"✅ Chapter {chapter}: Download completed!")
            logging.debug("Converting chapter %s to PDF", chapter)
            convert_chapter_to_pdf(folder)
            self.chapter_completed_map[chapter] = os.path.exists(
                get_pdf_output_path(folder)
            )
            yield from request_next_chapter(self, self.chapter_map)
