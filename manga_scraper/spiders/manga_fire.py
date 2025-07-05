import json
from urllib.parse import quote
import scrapy
from scrapy.http import HtmlResponse
from manga_scraper.items import MangaItem, SearchKeywordMangaLinkItem
from manga_scraper.spiders.common.config import ChapterParserConfig, MangaParserConfig
from manga_scraper.spiders.common.manga_page import parse_manga_page
from manga_scraper.utils.search_filter import select_manga_interactively


class MangaFireSpider(scrapy.Spider):
    """Spider for scraping manga data from mangafire.to"""

    name = "manga_fire"
    base_url = "https://mangafire.to"

    # Static parsing config
    manga_parser_config = MangaParserConfig.create_site_config(
        chapters_selector="ul li",
        chapter_id_extractor=lambda el: el.css("a::attr(data-id)").get(),
        chapter_number_extractor=lambda el: el.css("a::text")
        .get()
        .replace(":", "")
        .strip(),
        chapter_parser_config=ChapterParserConfig.create_site_config(
            page_urls_selector="",  # Not used here
            async_cleanup=False,
        ),
        use_playwright=False,
    )

    def __init__(self, search_term="a girl on the shore", **kwargs):
        super().__init__(**kwargs)
        self.search_term = search_term

    def start_requests(self):
        search_url = f"{self.base_url}/filter?keyword={quote(self.search_term)}&sort=most_relevance"
        yield scrapy.Request(
            url=search_url,
            callback=self.parse_search_page,
        )

    def parse_search_page(self, response):
        """Parse search result and request volume JSON"""
        manga_list = response.css("div.inner a.poster")

        selected_manga = select_manga_interactively(
            manga_list,
            manga_name_extractor=lambda el: el.css("div img::attr(alt)").get(),
        )

        manga_url = selected_manga.css("a::attr(href)").get()
        manga_id = manga_url.split(".")[-1]
        manga_name = selected_manga.css("div img::attr(alt)").get()

        yield MangaItem(
            manga_name=manga_name,
            manga_url=manga_url,
            manga_id=manga_id,
        )

        yield SearchKeywordMangaLinkItem(
            keyword=self.search_term,
            manga_id=manga_id,
            total_mangas=len(manga_list),
        )

        ajax_url = f"{self.base_url}/ajax/read/{manga_id}/volume/en"
        yield scrapy.Request(
            url=ajax_url,
            callback=self.process_json_response,
            meta={"manga_name": manga_name, "manga_id": manga_id, "spider": self},
        )

    def process_json_response(self, response):
        """Process volume list from JSON"""
        try:
            data = json.loads(response.text)
            if data.get("status") == 200 and "html" in data.get("result", {}):
                html_response = HtmlResponse(
                    url=response.url,
                    body=data["result"]["html"].encode("utf-8"),
                    encoding="utf-8",
                    request=response.request,
                )
                html_response.meta.update(response.meta)
                yield from parse_manga_page(html_response)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON: {e}")
