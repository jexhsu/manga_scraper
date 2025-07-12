# manga_scraper/spiders/common/manga_page.py
import requests
from manga_scraper.items import ChapterItem, MangaChapterLinkItem
from manga_scraper.spiders.common.chapter_page import parse_chapter_page
from manga_scraper.utils.chapter_filter import select_chapters_interactively
import json

from manga_scraper.utils.decrypt_content_key import decrypt_content_key
from manga_scraper.utils.js_var_extractor import extract_js_var
import urllib3

urllib3.disable_warnings()


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
    aes_key = extract_js_var(response)

    decrypted = decrypt_content_key(content_key, aes_key)

    filtered = select_chapters_interactively(
        decrypted,
        chapter_extractor=config["chapter_number_extractor"],
        debug_choice="g1(c(1)),g2(v(1)),g3(c(1))" if spider.debug_mode else None,
    )

    for chapter in filtered:
        chapter_id = chapter["id"]
        chapter_number = chapter["name"]
        chapter_url = f"/comic/{manga_id}/chapter/" + chapter_id
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
