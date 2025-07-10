# manga_scraper/pipelines/download_pdf.py
from collections import defaultdict
import os
from typing import Tuple
import img2pdf
import scrapy
import re

from manga_scraper.items import ChapterPageLinkItem, PageItem
from scrapy.pipelines.images import ImagesPipeline


class MangaDownloadPipeline(ImagesPipeline):
    """Pipeline for downloading manga pages and converting chapters to PDF."""

    def __init__(self, store_uri, download_func=None, settings=None):
        super().__init__(store_uri, download_func, settings)
        self.chapter_progress = defaultdict(int)  # Downloaded pages per chapter
        self.expected_pages = defaultdict(int)  # Total expected pages per chapter
        self.chapter_paths = defaultdict(str)  # Chapter storage paths

    def get_media_requests(self, item, info):
        """Yield requests for manga page images."""
        if isinstance(item, ChapterPageLinkItem):
            self.expected_pages[(item["manga_id"], item["chapter_id"])] = item[
                "total_pages"
            ]

        if isinstance(item, PageItem):
            manga_id = item["manga_id"]
            yield scrapy.Request(
                item["page_url"],
                headers={
                    "Referer": f"https://mangafire.to/ajax/read/{manga_id}/volume/en"
                },
                meta={
                    "manga_name": item["manga_name"],
                    "manga_id": manga_id,
                    "chapter_name": item["chapter_name"],
                    "chapter_id": item["chapter_id"],
                    "page_number": item["page_number"],
                },
            )

    def file_path(self, request, response=None, info=None, *, item=None):
        """Return the download path for a manga page."""
        manga_name, chapter_name = item["manga_name"], item["chapter_name"]
        manga_id, chapter_id = item["manga_id"], item["chapter_id"]
        clean_manga = manga_name
        clean_chapter = chapter_name

        # Store the chapter path for PDF conversion
        self.chapter_paths[(manga_id, chapter_id)] = os.path.join(
            self.store.basedir, clean_manga, clean_chapter
        )

        return f"{clean_manga}/{clean_chapter}/{request.meta['page_number']:03d}.jpg"

    def item_completed(self, results, item, info):
        """Handle completed downloads and trigger PDF conversion when ready."""
        if isinstance(item, PageItem):
            item["download_status"] = "completed"
            chapter_key = (item["manga_id"], item["chapter_id"])

            self.chapter_progress[chapter_key] += 1

            if self.chapter_progress[chapter_key] == self.expected_pages[chapter_key]:
                self._convert_chapter_to_pdf(chapter_key)

        return item

    @staticmethod
    def _chapter_name(id: str) -> str:
        """Clean and format chapter identifiers for filesystem use."""
        match = re.search(r"(chapter-\d+)$", id)
        return match.group(1) if match else id

    def _convert_chapter_to_pdf(self, chapter_key: Tuple[str, str]) -> None:
        """Convert downloaded images for a chapter into a PDF file."""
        chapter_path = self.chapter_paths.get(chapter_key)
        if not chapter_path or not os.path.exists(chapter_path):
            return

        # Get all sorted image files
        image_files = sorted(
            [
                file
                for file in os.listdir(chapter_path)
                if os.path.splitext(file)[1].lower()
                in {".jpg", ".jpeg", ".png", ".webp"}
            ],
            key=lambda x: int(
                "".join(filter(str.isdigit, x))
            ),  # Extract numbers for sorting
        )
        if not image_files:
            return

        # Create full paths and PDF filename
        image_paths = [os.path.join(chapter_path, img) for img in image_files]
        pdf_filename = os.path.join(
            os.path.dirname(chapter_path), f"{os.path.basename(chapter_path)}.pdf"
        )

        try:
            # Convert to PDF
            with open(pdf_filename, "wb") as f:
                f.write(img2pdf.convert(image_paths))
            print(f"Successfully created PDF: {pdf_filename}")

            # Cleanup original images
            for img_path in image_paths:
                os.remove(img_path)
            os.rmdir(chapter_path)

        except Exception as e:
            print(f"Failed to create PDF: {e}")
