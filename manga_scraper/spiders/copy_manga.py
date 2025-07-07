# manga_scraper/spiders/copy_manga.py
import json
import scrapy
from urllib.parse import urljoin
from manga_scraper.items import MangaItem, SearchKeywordMangaLinkItem
from manga_scraper.spiders.common.config import ChapterParserConfig, MangaParserConfig
from manga_scraper.spiders.common.manga_page import parse_manga_page
from manga_scraper.utils.search_filter import select_manga_interactively
from scrapy_playwright.page import PageMethod


class CopyMangaSpider(scrapy.Spider):
    name = "copy_manga"
    base_url = "https://www.copy20.com"

    # Placeholders for future use
    manga_parser_config = MangaParserConfig.create_site_config(
        chapter_number_extractor=lambda c: c.get("name", ""),
        chapter_parser_config=ChapterParserConfig.create_site_config(
            content_key_selector="div.imageData::attr(contentkey)",  # Define if needed later
        ),
    )

    def __init__(self, search_term="错位的青春", **kwargs):
        super().__init__(**kwargs)
        self.search_term = search_term

    def start_requests(self):
        url = f"{self.base_url}/api/kb/web/searchbq/comics?offset=0&platform=2&limit=12&q={self.search_term}&q_type="

        yield scrapy.Request(
            url=url,
            callback=self.parse_search_preview,
            headers={
                "Accept": "*/*",
            },
            meta={"skip_fake_ua_middleware": True},
        )

    def parse_search_preview(self, response):
        data = json.loads(response.text)

        results = data.get("results", {})
        manga_list = results.get("list", [])

        search_items = [
            {"name": manga.get("name", ""), "path_word": manga.get("path_word", "")}
            for manga in manga_list
        ]

        selected = select_manga_interactively(
            search_items, manga_name_extractor=lambda el: el["name"]
        )

        manga_name = selected["name"]
        manga_id = selected["path_word"]
        manga_url = urljoin(self.base_url, f"/comic/{manga_id}")

        yield MangaItem(
            manga_name=manga_name,
            manga_url=manga_url,
            manga_id=manga_id,
        )

        yield SearchKeywordMangaLinkItem(
            keyword=self.search_term,
            manga_id=manga_id,
            total_mangas=len(search_items),
        )

        yield scrapy.Request(
            url=manga_url,
            callback=parse_manga_page,
            headers={
                "Accept": "*/*",
            },
            meta={
                "manga_name": manga_name,
                "manga_id": manga_id,
                "spider": self,
                "skip_fake_ua_middleware": True,
            },
        )
