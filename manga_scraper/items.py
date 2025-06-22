# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from enum import Enum


class DownloadStatus(Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"


class MangaItem(scrapy.Item):
    # Basic info
    manga_id = scrapy.Field()
    manga_name = scrapy.Field()
    manga_url = scrapy.Field()

    # Download progress
    total_chapters = scrapy.Field()
    downloaded_chapters = scrapy.Field()
    download_status = scrapy.Field()


class ChapterItem(scrapy.Item):
    # Basic info
    manga_id = scrapy.Field()
    chapter_id = scrapy.Field()
    chapter_number_name = scrapy.Field()
    chapter_text_name = scrapy.Field()
    chapter_name = scrapy.Field()
    chapter_url = scrapy.Field()

    # Download progress
    chapter_number = scrapy.Field()
    total_pages = scrapy.Field()
    downloaded_pages = scrapy.Field()
    download_status = scrapy.Field()
    download_path = scrapy.Field()


class PageItem(scrapy.Item):
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
