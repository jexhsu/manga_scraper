import json
from urllib.parse import quote
import scrapy
import os
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

    def __init__(
        self, search_term="a girl on the shore", debug=False, language=None, **kwargs
    ):
        super().__init__(**kwargs)
        self.search_term = search_term
        self.debug_mode = str(debug).lower() in ("true", "1", "yes")

        # Apply default language if in debug mode
        if self.debug_mode and language is None:
            self.language = "en"
        elif language in ("en", "ja"):
            self.language = language
        else:
            raise ValueError("`language` must be either 'en' or 'ja'")

    def start_requests(self):
        search_url = f"{self.base_url}/filter?keyword={quote(self.search_term)}&sort=most_relevance"
        ajax_url = (
            f"{self.base_url}/ajax/manga/search?keyword={quote(self.search_term)}"
        )
        yield scrapy.Request(
            url=search_url,
            callback=self._handle_search_response,
            errback=lambda failure: self._fallback_to_ajax(failure, ajax_url),
        )

    def _fallback_to_ajax(self, failure, ajax_url):
        self.logger.warning(
            f"Search URL failed ({failure.value}), falling back to AJAX"
        )
        yield scrapy.Request(url=ajax_url, callback=self._process_search_json)

    def _handle_search_response(self, response):
        """Detect response type and parse accordingly."""
        content_type = response.headers.get("Content-Type", b"").decode()
        if "application/json" in content_type:
            yield from self._process_search_json(response)
        else:
            yield from self._parse_search_html(response)

    def _parse_search_html(self, response):
        """Parse search result and request volume JSON"""
        manga_list = response.css("div.inner a.poster")

        selected_manga = select_manga_interactively(
            manga_list,
            manga_name_extractor=lambda el: el.css("div img::attr(alt)").get(),
            debug_choice=0 if self.debug_mode else None,
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
        ajax_url = f"{self.base_url}/ajax/read/{manga_id}/volume/{self.language}"
        yield scrapy.Request(
            url=ajax_url,
            callback=self._process_volume_json,
            meta={"manga_name": manga_name, "manga_id": manga_id, "spider": self},
        )

    def _process_json_response(self, response, log_prefix="JSON"):
        """Generic JSON response handler that extracts HTML and calls callback."""
        try:
            data = json.loads(response.text)
            if data.get("status") == 200:
                html = data.get("result", {}).get("html")
                html_response = HtmlResponse(
                    url=response.url,
                    body=html.encode(),
                    encoding="utf-8",
                    request=response.request,
                )
                html_response.meta.update(response.meta)
                yield from self._parse_search_html(html_response)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse {log_prefix} JSON: {e}")

    def _process_search_json(self, response):
        yield from self._process_json_response(response, "search")

    def s_process_json_response(self, response, log_prefix="JSON"):
        """Generic JSON response handler that extracts HTML and calls callback."""
        try:
            data = json.loads(response.text)
            if data.get("status") == 200:
                html = data.get("result", {}).get("html")
                html_response = HtmlResponse(
                    url=response.url,
                    body=html.encode(),
                    encoding="utf-8",
                    request=response.request,
                )
                html_response.meta.update(response.meta)
                yield from parse_manga_page(html_response)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse {log_prefix} JSON: {e}")

    def _process_volume_json(self, response):
        yield from self.s_process_json_response(response, "volume")
