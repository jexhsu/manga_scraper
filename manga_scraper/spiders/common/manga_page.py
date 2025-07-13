from manga_scraper.items import ChapterItem, MangaChapterLinkItem
from manga_scraper.spiders.common.chapter_page import parse_chapter_page
from manga_scraper.utils.chapter_filter import select_chapters_interactively
from manga_scraper.utils.playwright_config import setup_playwright


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

    page_urls_selector = site_config["chapter_parser_config"]["page_urls_selector"]
    wait_for = page_urls_selector.rpartition(" ")[0]

    sel = selector or response
    raw_chapters = sel.css(site_config["chapters_selector"])

    filtered_chapters = select_chapters_interactively(
        raw_chapters,
        chapter_extractor=site_config["chapter_number_extractor"],
        debug_mode=spider.debug_mode,
    )

    for chapter in filtered_chapters:
        chapter_url = chapter.css("a::attr(href)").get()
        chapter_id = site_config["chapter_id_extractor"](chapter_url)

        yield ChapterItem(
            manga_id=manga_id,
            chapter_id=chapter_id,
            chapter_url=chapter_url,
            chapter_number_name=site_config["chapter_number_extractor"](chapter),
            chapter_text_name=site_config["chapter_text_extractor"](chapter),
        )

        yield MangaChapterLinkItem(
            manga_id=manga_id,
            chapter_id=chapter_id,
            total_chapters=len(raw_chapters),
        )

        meta = {
            "manga_id": manga_id,
            "chapter_id": chapter_id,
            "spider": spider,
        }

        if site_config.get("use_playwright", False):
            meta.update(setup_playwright(wait_for))

        cookies = spider.cookies if site_config.get("use_cookie", False) else None

        yield response.follow(
            chapter_url,
            callback=parse_chapter_page,
            cookies=cookies,
            meta=meta,
        )
