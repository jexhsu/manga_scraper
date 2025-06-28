from manga_scraper.spiders.common.chapter_page import parse_chapter_page
from manga_scraper.utils.playwright_config import get_chapter_page_meta


def parse_manga_page(response, selector=None):
    """
    Parse manga listing page to extract chapter links and metadata.

    Args:
        response (scrapy.http.Response): The Scrapy response object.
        selector (scrapy.Selector, optional): Custom selector (e.g., from Playwright page content).
            If None, defaults to response.css.

    Yields:
        dict: Chapter metadata.
        scrapy.Request: Request to parse the chapter page.
    """
    manga_id = response.meta["manga_id"]
    spider = response.meta.get("spider")

    site_config = spider.manga_parser_config

    sel = selector or response
    chapters = sel.css(site_config["chapters_selector"])

    for chapter in chapters[-1:]:
        chapter_url = chapter.css("a::attr(href)").get()
        chapter_id = site_config["chapter_id_extractor"](chapter_url)

        yield {
            "manga_id": manga_id,
            "chapter_id": chapter_id,
            "chapter_url": chapter_url,
            "chapter_number": site_config["chapter_number_extractor"](chapter),
            "chapter_text": site_config["chapter_text_extractor"](chapter),
        }

        meta = {
            "manga_id": manga_id,
            "chapter_id": chapter_id,
            "spider": spider,
        }

        if site_config.get("use_playwright_meta", False):
            meta.update(get_chapter_page_meta(manga_id=manga_id, chapter_id=chapter_id))

        yield response.follow(
            chapter_url,
            callback=parse_chapter_page,
            meta=meta,
        )
