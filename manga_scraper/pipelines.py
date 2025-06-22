# manga_scraper/pipelines.py
import json
from datetime import datetime
from urllib.parse import urljoin, urlparse
import hashlib

from manga_scraper.items import ChapterItem, MangaItem, PageItem


import hashlib

from manga_scraper.settings import BASE_URL


class MangaDataCleaningPipeline:
    def process_item(self, item, spider):
        if "manga_name" in item:
            return self._clean_manga_data(item)
        elif "chapter_number_name" in item:
            return self._clean_chapter_data(item)
        elif "page_url" in item:
            return self._clean_image_data(item)
        return item

    def _clean_manga_data(self, item):
        """Clean and process manga data."""
        item["manga_name"] = item["manga_name"].strip()
        item["manga_url"] = self._get_full_url(item["manga_url"])
        item["manga_id"] = self._generate_id(item["manga_url"])
        item["download_status"] = "pending"
        return item

    def _clean_chapter_data(self, item):
        """Clean and process chapter data."""
        item["chapter_name"] = self._generate_chapter_name(item)
        item["chapter_url"] = self._get_full_url(item["chapter_url"])
        item["chapter_id"] = self._generate_id(item["chapter_url"])
        item["download_status"] = "pending"
        return item

    def _clean_image_data(self, item):
        """Clean and process image data."""
        item["page_url"] = self._get_full_url(item["page_url"])
        item["page_id"] = self._generate_id(item["page_url"])
        item["download_status"] = "pending"
        item["retry_count"] = item.get("retry_count", 0)
        return item

    def _get_full_url(self, relative_url):
        """Convert relative URL to absolute URL and clean it."""
        return urljoin(BASE_URL, relative_url).partition("?")[0]

    def _generate_chapter_name(self, item):
        """Combine chapter number and text to create full chapter name."""
        number = item.get("chapter_number_name", "")
        text = item.get("chapter_text_name", "")
        return number if not text else number + text

    def _generate_id(self, url):
        """Generate MD5 hash ID from URL."""
        return hashlib.md5(url.encode()).hexdigest() if url else None


class MangaJsonExportPipeline:
    def open_spider(self, spider):
        self.manga_data = {}
        self.current_manga_id = None

    def close_spider(self, spider):
        # Write final JSON output
        with open("manga_data.json", "w") as f:
            json.dump(list(self.manga_data.values()), f, indent=4)

    def process_item(self, item, spider):
        if isinstance(item, MangaItem):
            self._process_manga_item(item)
        elif isinstance(item, ChapterItem):
            self._process_chapter_item(item)
        elif isinstance(item, PageItem):
            self._process_page_item(item)
        return item

    def _process_manga_item(self, item):
        if item["manga_id"] not in self.manga_data:
            self.manga_data[item["manga_id"]] = {
                "manga_id": item["manga_id"],
                "manga_name": item["manga_name"],
                "manga_url": item["manga_url"],
                "download_status": item["download_status"],
                "chapters": [],
                "created_at": datetime.now().isoformat(),
            }
        self.current_manga_id = item["manga_id"]

    def _process_chapter_item(self, item):
        if not self.current_manga_id:
            return

        chapter_data = {
            "chapter_id": item["chapter_id"],
            "chapter_name": item["chapter_name"],
            "chapter_url": item["chapter_url"],
            "download_status": item["download_status"],
            "pages": [],
            "created_at": datetime.now().isoformat(),
        }

        # Add chapter to current manga
        if self.current_manga_id in self.manga_data:
            self.manga_data[self.current_manga_id]["chapters"].append(chapter_data)

    def _process_page_item(self, item):
        if not self.current_manga_id or not self.manga_data.get(self.current_manga_id):
            return

        # Get last chapter (most recently added)
        manga = self.manga_data[self.current_manga_id]
        if not manga["chapters"]:
            return

        chapter = manga["chapters"][-1]

        # Add page to chapter
        chapter["pages"].append(
            {
                "page_id": item["page_id"],
                "page_url": item["page_url"],
                "page_number": len(chapter["pages"]) + 1,
                "download_status": item["download_status"],
                "retry_count": item.get("retry_count", 0),
                "created_at": datetime.now().isoformat(),
            }
        )

        # Update chapter page count
        chapter["total_pages"] = len(chapter["pages"])

        # Update manga chapter count
        manga["total_chapters"] = len(manga["chapters"])
