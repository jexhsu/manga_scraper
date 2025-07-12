# manga_scraper/spiders/common/.py
import json
from pprint import pprint
from manga_scraper.items import ChapterItem, MangaChapterLinkItem
from manga_scraper.spiders.common.chapter_page import parse_chapter_page
from manga_scraper.utils.chapter_filter import select_chapters_interactively
from manga_scraper.utils.chapter_parser import parse_manga_groups


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

    chapter_xpath = """
        //h4[contains(span/text(), "单话")]/following-sibling::div[contains(@class, "chapter-list") and not(preceding-sibling::div[1][contains(@class, "chapter-list")])][1]
    """
    volume_xpath = """
        //h4[contains(span/text(), "单行本")]/following-sibling::*[1][self::div[contains(@class, "chapter-list")]]
    """
    extra_xpath = """
        //h4[contains(span/text(), "番外篇")]/following-sibling::*[1][self::div[contains(@class, "chapter-list")]]
    """

    data = parse_manga_groups(response, chapter_xpath, volume_xpath, extra_xpath)
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    filtered = select_chapters_interactively(
        data,
        chapter_extractor=config["chapter_number_extractor"],
        debug_choice="g1(c(1)),g2(v(1)),g3(e(1))" if spider.debug_mode else None,
    )

    for chapter in filtered:
        chapter_id = chapter["id"]
        chapter_number = chapter["name"]
        chapter_url = f"/comic/{manga_id}/{chapter_id}.html"
        chapter_group = chapter["group"]
        chapter_type = chapter["type"]

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
        )

        yield response.follow(
            url=chapter_url,
            callback=parse_chapter_page,
            meta={
                "manga_name": manga_name,
                "manga_id": manga_id,
                "chapter_number_name": chapter_number,
                "chapter_id": chapter_id,
                "spider": spider,
                "chapter_group": chapter_group,
                "chapter_type": chapter_type,
            },
        )
