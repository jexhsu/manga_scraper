# manga_scraper/pipelines/data_cleaning.py
from urllib.parse import urljoin
from manga_scraper.items import (
    ChapterItem,
    ChapterPageLinkItem,
    MangaChapterLinkItem,
    MangaItem,
    PageItem,
    SearchKeywordMangaLinkItem,
)
from manga_scraper.settings import BASE_URL


class MangaDataCleaningPipeline:
    def process_item(self, item, spider):
        if isinstance(item, SearchKeywordMangaLinkItem):
            return item
        elif isinstance(item, MangaChapterLinkItem):
            return item
        elif isinstance(item, ChapterPageLinkItem):
            return item
        elif isinstance(item, MangaItem):
            self._clean_manga_data(item)
        elif isinstance(item, ChapterItem):
            self._clean_chapter_data(item)
        elif isinstance(item, PageItem):
            self._clean_image_data(item)
        return item

    def _clean_manga_data(self, item):
        """Clean and process manga data."""
        item["manga_name"] = item["manga_name"].strip()
        item["manga_url"] = self._get_full_url(item["manga_url"])
        return item

    def _clean_chapter_data(self, item):
        """Clean and process chapter data."""
        item["chapter_name"] = self._generate_chapter_name(item)
        item["chapter_url"] = self._get_full_url(item["chapter_url"])
        return item

    def _clean_image_data(self, item):
        """Clean and process image data."""
        return item

    def _get_full_url(self, relative_url):
        """Convert relative URL to absolute URL and clean it."""
        return urljoin(BASE_URL, relative_url).partition("?")[0]

    def _generate_chapter_name(self, item):
        """Combine chapter number and text to create full chapter name."""
        number = item.get("chapter_number_name", "").strip()
        text = item.get("chapter_text_name")
        if text is None or not str(text).strip():
            return number
        return f"{number} {text.strip()}"
