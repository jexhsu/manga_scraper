# manga_scraper/spiders/parse_manga.py
from random import randint
from manga_scraper.items import ChapterItem, MangaChapterLinkItem, MangaItem

from manga_scraper.utils.playwright_config import get_chapter_page_meta
from .chapter_page import parse_chapter_page


def parse_manga_page(response):
    manga_id = response.meta["manga_id"]
    chapters = response.css("div[data-name='chapter-list'] [q\\:key='8t_8']")

    chapters_to_process = chapters[-randint(1, 3) :]

    for chapter in chapters_to_process:
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

        yield response.follow(
            chapter_url,
            callback=parse_chapter_page,
            meta=get_chapter_page_meta(
                manga_id=manga_id,
                chapter_id=chapter_id,
            ),
        )
