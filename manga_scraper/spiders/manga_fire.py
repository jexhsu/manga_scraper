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

    # Headers for mimicking browser request
    custom_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://mangafire.to/",
    }

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
        headers = {
            "Host": "mangafire.to",
            "Cookie": "remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d=549750%7CH0JhJqniuzjnmtQih1QYM7rtA6OsZWl0tW61P3h2aqlokGkpXvk86rNYpqUX%7C%242y%2412%244dT2swzWIBfkLE.qtIEhEusSwtgfn2jsW4sMB7xyEB8R7oE2u0Jj6; usertype=user; session=Ngo3YXVLWWfFokscXcW7v6m0wdzH5wgtxlzHeuDc; cf_clearance=yhg1ZEKPF87_s5bA8AmfybYjsD7L5r7ht__fsD8KIf0-1751705865-1.2.1.1-LLSObVijq77bDX_sOFCDAIB2.JJvNSmBryp4UhGntwbxIdlIa7EbI8ynd8P5q6_QIH6O.4BKJ81CCCondASDNwGGrG7BrsKTWYgag4OWaWnvmw3R8aU2q4fDMwbv4VzATuJeJodhty42bFzNzvQ0q8exl7hbUQsI3x_G78b0DiSC66ruVpXYFYh8P4Q_2FQddCgDozZg07jMX2GRk7EtNrkQmcFqU6R2Iz5nQdHgC5U",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9,ja;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Sec-CH-UA": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Platform": '"macOS"',
            "Priority": "u=0, i",
        }
        yield scrapy.Request(
            url=search_url,
            callback=self.parse_search_page,
            headers=headers,
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
