# manga_scraper/spiders/common/chapter_page.py
import json
from manga_scraper.items import PageItem, ChapterPageLinkItem
from manga_scraper.spiders.common.config import MangaParserConfig
from manga_scraper.utils.image_extractor import extract_manhua_image_urls


def parse_chapter_page(response):
    """
    Parse image URLs from chapter AJAX response (JSON format).

    Args:
        response (scrapy.Response): JSON response from chapter endpoint.
    """
    spider = response.meta["spider"]
    manga_id = response.meta["manga_id"]
    manga_name = response.meta["manga_name"]
    chapter_group = response.meta["chapter_group"]
    chapter_type = response.meta["chapter_type"]
    chapter_id = response.meta["chapter_id"]
    chapter_number_name = response.meta["chapter_number_name"]

    urls = extract_manhua_image_urls(response)
    page_urls = urls[:1] if spider.debug_mode else None

    for idx, url in enumerate(page_urls, start=1):
        yield PageItem(
            manga_name=manga_name,
            manga_id=manga_id,
            chapter_name=chapter_number_name,
            chapter_id=chapter_id,
            chapter_group=chapter_group,
            chapter_type=chapter_type,
            page_number=idx,
            page_url=url,
        )

        yield ChapterPageLinkItem(
            manga_id=manga_id,
            chapter_id=chapter_id,
            page_id=idx,
            total_pages=len(page_urls),
        )
