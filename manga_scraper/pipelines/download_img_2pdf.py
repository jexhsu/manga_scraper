from collections import defaultdict
import os
from typing import Tuple
import img2pdf
import scrapy
import re
from PIL import Image, ImageEnhance  # Added for image quality enhancement

from manga_scraper.items import ChapterPageLinkItem, PageItem
from scrapy.pipelines.images import ImagesPipeline


class MangaDownloadPipeline(ImagesPipeline):
    """Pipeline for downloading manga pages, enhancing image quality, and converting chapters to PDF."""

    def __init__(self, store_uri, download_func=None, settings=None):
        super().__init__(store_uri, download_func, settings)
        self.chapter_progress = defaultdict(int)  # Downloaded pages per chapter
        self.expected_pages = defaultdict(int)  # Total expected pages per chapter
        self.chapter_paths = defaultdict(str)  # Chapter storage paths
        # Enhancement parameters (adjust as needed)
        self.enhance_sharpness = 1.2  # Sharpness factor (1.0 = original)
        self.enhance_contrast = 1.1  # Contrast factor (1.0 = original)

    def get_media_requests(self, item, info):
        """Yield requests for manga page images."""
        if isinstance(item, ChapterPageLinkItem):
            self.expected_pages[(item["manga_id"], item["chapter_id"])] = item[
                "total_pages"
            ]

        if isinstance(item, PageItem):
            chapter_id = (item["chapter_id"],)
            yield scrapy.Request(
                item["page_url"],
                headers={
                    "Referer": f"https://weebcentral.com/chapters/{chapter_id}/images?is_prev=False&current_page=1&reading_style=long_strip&reading_style=long_strip"
                },
                meta={
                    "manga_name": item["manga_name"],
                    "manga_id": item["manga_id"],
                    "chapter_name": item["chapter_name"],
                    "chapter_id": chapter_id,
                    "chapter_type": item["chapter_type"],
                    "page_number": item["page_number"],
                },
            )

    def file_path(self, request, response=None, info=None, *, item=None):
        """Return the download path for a manga page."""
        chapter_type_map = {
            1: "話",   # Chapters
            2: "卷",     # Volumes
            3: "番外",   # Extras
        }
        manga_name, chapter_type, chapter_name = item["manga_name"], item["chapter_type"], item["chapter_name"]
        manga_id, chapter_id = item["manga_id"], item["chapter_id"]
        clean_manga = self._clean_name(manga_name)
        chapter_type = chapter_type_map.get(item["chapter_type"], "未知类型")
        clean_chapter = self._chapter_name(chapter_name)


        # Store the chapter path for PDF conversion
        self.chapter_paths[(manga_id, chapter_id)] = os.path.join(
            self.store.basedir, clean_manga, chapter_type, clean_chapter
        )

        return f"{clean_manga}/{chapter_type}/{clean_chapter}/{request.meta['page_number']:03d}.jpg"

    def _enhance_image_quality(self, image_path: str) -> None:
        """
        Enhance the quality of downloaded manga images.
        Applies sharpening and contrast adjustments to improve readability.
        
        Args:
            image_path: Path to the image file to be enhanced
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if needed (for JPEG compatibility)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Apply image enhancements
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(self.enhance_sharpness)
                
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(self.enhance_contrast)
                
                # Save the enhanced image (overwrite original)
                img.save(image_path, quality=95, optimize=True)
                
        except Exception as e:
            print(f"Error enhancing image {image_path}: {e}")

    def item_completed(self, results, item, info):
        """Handle completed downloads, enhance images, and trigger PDF conversion when ready."""
        if isinstance(item, PageItem):
            item["download_status"] = "completed"
            chapter_key = (item["manga_id"], item["chapter_id"])

            # Get the downloaded file path from results
            for success, file_info in results:
                if success:
                    image_path = file_info['path']
                    full_path = os.path.join(self.store.basedir, image_path)
                    self._enhance_image_quality(full_path)

            self.chapter_progress[chapter_key] += 1

            if self.chapter_progress[chapter_key] == self.expected_pages[chapter_key]:
                self._convert_chapter_to_pdf(chapter_key)

        return item

    @staticmethod
    def _clean_name(id: str) -> str:
        """Clean and format manga/chapter identifiers for filesystem use."""
        return id.split("-", 1)[-1] if "-" in id else id

    @staticmethod
    def _chapter_name(id: str) -> str:
        """Clean and format chapter identifiers for filesystem use."""
        match = re.search(r"(chapter-\d+)$", id)
        return match.group(1) if match else id

    def _convert_chapter_to_pdf(self, chapter_key: Tuple[str, str]) -> None:
        """Convert downloaded and enhanced images for a chapter into a PDF file."""
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