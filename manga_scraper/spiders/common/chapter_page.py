# manga_scraper/spiders/common/chapter_page.py
from manga_scraper.items import PageItem, ChapterPageLinkItem
from manga_scraper.spiders.common.config import MangaParserConfig


def parse_chapter_page(response):
    """
    Parse image URLs from chapter AJAX response (JSON format).

    Args:
        response (scrapy.Response): JSON response from chapter endpoint.
    """
    spider = response.meta["spider"]
    manga_id = response.meta["manga_id"]
    manga_name = response.meta["manga_name"]
    chapter_id = response.meta["chapter_id"]
    chapter_number_name = response.meta["chapter_number_name"]

    config = spider.manga_parser_config["chapter_parser_config"]
    page_urls = response.css(config["page_urls_selector"]).getall()

    for idx, url in enumerate(page_urls, start=1):
        yield PageItem(
            manga_name=manga_name,
            manga_id=manga_id,
            chapter_name=chapter_number_name,
            chapter_id=chapter_id,
            page_number=idx,
            page_url=url,
        )

        yield ChapterPageLinkItem(
            manga_id=manga_id,
            chapter_id=chapter_id,
            page_id=idx,
            total_pages=len(page_urls),
        )
