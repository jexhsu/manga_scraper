# manga_scraper/spiders/parse_chapter.py
from manga_scraper.items import ChapterPageLinkItem, PageItem
from pprint import pprint

from manga_scraper.utils.html_parser import extract_urls_from_qwik_json


async def parse_chapter_page(response):
    """
    Parse chapter page using configuration from spider instance in response meta
    Args:
        response: Scrapy response object with spider instance in meta
    """
    spider = response.meta.get("spider")
    chapter_id = response.meta["chapter_id"]
    manga_id = response.meta["manga_id"]

    # Get config from spider's manga parser config
    config = spider.manga_parser_config["chapter_parser_config"]

    if spider.manga_parser_config["use_cookie"]:
        urls = extract_urls_from_qwik_json(response)
    else:
        urls = (
            config["page_urls_extractor"](response)
            if config.get("page_urls_extractor") is not None
            else response.css(config["page_urls_selector"]).getall()
        )

    page_urls = urls[:1] if spider.debug_mode else None

    for idx, url in enumerate(page_urls, start=1):
        yield PageItem(
            manga_id=manga_id,
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

    if config.get("async_cleanup", False) and "playwright_page" in response.meta:
        await response.meta["playwright_page"].close()
