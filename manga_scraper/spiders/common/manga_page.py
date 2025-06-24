# manga_scraper/spiders/parse_manga.py
from urllib.parse import urljoin
from manga_scraper.items import ChapterItem, MangaChapterLinkItem
import scrapy
from scrapy_playwright.page import PageMethod
from .chapter_page import parse_chapter_page
from manga_scraper.items import MangaItem


def parse_manga_page(response):
    chapters = response.css("div[data-name='chapter-list'] [q\\:key='8t_8']")[-3:]
    manga_id = response.meta["manga_id"]
    for chapter in chapters:
        chapter_url = chapter.css("a::attr(href)").get()
        chapter_id = chapter_url.split("/")[-1]
        yield ChapterItem(
            manga_id=manga_id,
            chapter_id=chapter_id,
            chapter_url=chapter_url,
            chapter_number_name=chapter.css("a::text").get(),
            chapter_text_name=chapter.css("span[q\\:key='8t_1']::text").get(),
        )
        yield MangaChapterLinkItem(
            manga_id=manga_id,
            chapter_id=chapter_id,
            total_chapters=len(chapters),
        )
        yield scrapy.Request(
            urljoin(response.url, chapter_url),
            callback=parse_chapter_page,
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod(
                        "wait_for_selector",
                        "div[data-name='image-item']",
                        timeout=600000,
                    ),
                    PageMethod(
                        "evaluate",
                        "() => { window.stop(); }",
                    ),
                ],
                "playwright_page_goto_kwargs": {
                    "wait_until": "domcontentloaded",
                    "timeout": 600000,
                },
                "playwright_include_page": True,
                "manga_id": manga_id,
                "chapter_id": chapter_id,
            },
        )
