# manga_scraper/spiders/common/manga_page.py
import requests
from manga_scraper.items import ChapterItem, MangaChapterLinkItem
from manga_scraper.spiders.common.chapter_page import parse_chapter_page
from manga_scraper.utils.chapter_filter import select_chapters_interactively
import json

from manga_scraper.utils.decrypt_content_key import decrypt_content_key
from manga_scraper.utils.js_var_extractor import extract_js_var

def parse_manga_page(
    response,
):
    """
    Parse volume list HTML and yield chapters.

    Args:
        response (scrapy.Response): Response containing injected HTML.
    """
    spider = response.meta.get("spider")
    manga_id = response.meta["manga_id"]
    manga_name = response.meta["manga_name"]
    config = spider.manga_parser_config

    content_key_response = requests.get(
        f"{spider.base_url}/comicdetail/{manga_id}/chapters",
        headers={
            "Accept": "*/*",
        },
        verify=False,
    )

    content_key = json.loads(content_key_response.text).get("results", "")
    dio_key = extract_js_var(response, "dio")

    decrypted = decrypt_content_key(content_key, dio_key)

    chapters_by_group = decrypted.get("groups", {})

    raw_chapters = []
    for group in chapters_by_group.values():
        raw_chapters.extend(group.get("chapters", []))

    filtered = select_chapters_interactively(
        raw_chapters, chapter_extractor=config["chapter_number_extractor"]
    )

    for chapter in filtered:
        chapter_id = chapter["id"]
        chapter_number = chapter["name"]
        chapter_url = "/comic/jinjidejuren/chapter/" + chapter_id
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
            total_chapters=len(raw_chapters),
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
                "chapter_type": chapter_type
            },
        )
