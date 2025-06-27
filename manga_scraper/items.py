# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from enum import Enum


class DownloadStatus(Enum):
    COMPLETED = "completed"
    FAILED = "failed"


class BaseItem(scrapy.Item):
    """Base class for all items that automatically adds item_type"""

    item_type = scrapy.Field()  # Explicitly declare the field

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["item_type"] = self.__class__.__name__


class SearchKeywordMangaLinkItem(BaseItem):
    keyword = scrapy.Field()
    manga_id = scrapy.Field()
    total_mangas = scrapy.Field()


class MangaItem(BaseItem):
    # Basic info
    keyword = scrapy.Field()
    manga_id = scrapy.Field()
    manga_name = scrapy.Field()
    manga_url = scrapy.Field()
    manga_follows = scrapy.Field()
    total_chapters = scrapy.Field()

    # Download progress
    total_chapters = scrapy.Field()
    downloaded_chapters = scrapy.Field()
    download_status = scrapy.Field()


class MangaChapterLinkItem(BaseItem):
    manga_id = scrapy.Field()
    chapter_id = scrapy.Field()
    total_chapters = scrapy.Field()


class ChapterItem(BaseItem):
    # Basic info
    manga_id = scrapy.Field()
    chapter_id = scrapy.Field()
    chapter_number_name = scrapy.Field()
    chapter_text_name = scrapy.Field()
    chapter_name = scrapy.Field()
    chapter_url = scrapy.Field()
    total_pages = scrapy.Field()

    # Download progress
    chapter_number = scrapy.Field()
    total_pages = scrapy.Field()
    downloaded_pages = scrapy.Field()
    download_status = scrapy.Field()
    pdf_path = scrapy.Field()


class ChapterPageLinkItem(BaseItem):
    manga_id = scrapy.Field()
    chapter_id = scrapy.Field()
    page_id = scrapy.Field()
    total_pages = scrapy.Field()


class PageItem(BaseItem):
    # Basic info
    manga_id = scrapy.Field()
    chapter_id = scrapy.Field()
    page_id = scrapy.Field()
    page_url = scrapy.Field()

    # Download progress
    page_number = scrapy.Field()
    download_status = scrapy.Field()
    file_path = scrapy.Field()

    # For retry/failure handling
    retry_count = scrapy.Field()
