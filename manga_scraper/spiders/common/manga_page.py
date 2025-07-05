from manga_scraper.items import ChapterItem, MangaChapterLinkItem
from manga_scraper.spiders.common.config import MangaParserConfig
from manga_scraper.spiders.common.chapter_page import parse_chapter_page
from manga_scraper.utils.chapter_filter import select_chapters_interactively


def parse_manga_page(
    response,
):
    """
    Parse volume list HTML and yield chapters.

    Args:
        response (scrapy.Response): Response containing injected HTML.
    """
    manga_name = response.meta["manga_name"]
    manga_id = response.meta["manga_id"]
    spider = response.meta.get("spider")
    config = spider.manga_parser_config
    raw_chapters = response.css(config["chapters_selector"])

    filtered = select_chapters_interactively(
        raw_chapters, chapter_extractor=config["chapter_number_extractor"]
    )

    for chapter in filtered:
        chapter_url = chapter.css("a::attr(href)").get()
        chapter_id = config["chapter_id_extractor"](chapter)
        chapter_number = config["chapter_number_extractor"](chapter)

        yield ChapterItem(
            manga_name=manga_name,
            manga_id=manga_id,
            chapter_number_name=chapter_number,
            chapter_id=chapter_id,
            chapter_url=chapter_url,
        )

        yield MangaChapterLinkItem(
            manga_id=manga_id,
            chapter_id=chapter_id,
            total_chapters=len(raw_chapters),
        )

        yield response.follow(
            url=f"{spider.base_url}/ajax/read/volume/{chapter_id}",
            callback=parse_chapter_page,
            meta={
                "manga_name": manga_name,
                "manga_id": manga_id,
                "chapter_number_name": chapter_number,
                "chapter_id": chapter_id,
                "spider": spider,
            },
        )
