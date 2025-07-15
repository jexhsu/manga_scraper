# manga_scraper/spiders/manhuagui.py
from urllib.parse import quote
import scrapy
from scrapy.http import HtmlResponse
from manga_scraper.items import MangaItem, SearchKeywordMangaLinkItem
from manga_scraper.spiders.common.config import ChapterParserConfig, MangaParserConfig
from manga_scraper.spiders.common.manga_page import parse_manga_page
from manga_scraper.utils.search_filter import select_manga_interactively
from manga_scraper.utils.lzstring import LZString
from urllib.parse import urljoin


class ManhuaGuiSpider(scrapy.Spider):
    """Spider for scraping manga data from manhuagui.com"""

    name = "manhuagui"
    # TODO: Add __init__ parameter 'sp' or 'td' to switch between simplified/traditional Chinese
    # "https://tw.manhuagui.com"  # Traditional Chinese site URL
    base_url = "https://www.manhuagui.com"

    # Static parsing config
    manga_parser_config = MangaParserConfig.create_site_config(
        chapters_selector="ul li",
        chapter_id_extractor=lambda el: el.css("a::attr(data-id)").get(),
        chapter_number_extractor=lambda c: c.get("name", ""),
        chapter_parser_config=ChapterParserConfig.create_site_config(
            page_urls_selector="",  # Not used here
        ),
    )

    def __init__(self, search_term="进击的巨人", debug=False, **kwargs):
        super().__init__(**kwargs)
        self.search_term = search_term
        self.debug_mode = str(debug).lower() in ("true", "1", "yes")

    def start_requests(self):
        search_url = f"{self.base_url}/s/{quote(self.search_term)}_o1.html"
        yield scrapy.Request(
            url=search_url,
            callback=self.parse_search_page,
        )

    def parse_search_page(self, response):
        """Parse search result and request volume JSON"""
        manga_list = response.css("div.book-result ul li.cf div.book-cover")

        selected_manga = select_manga_interactively(
            manga_list,
            manga_name_extractor=lambda el: el.css("a::attr(title)").get(),
            debug_choice=0 if self.debug_mode else None,
        )

        manga_url = selected_manga.css("a::attr(href)").get()
        manga_id = manga_url.split("/")[-2]
        manga_name = selected_manga.css("a::attr(title)").get()

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

        yield scrapy.Request(
            url=urljoin(self.base_url, manga_url),
            callback=self.parse_manga_html,
            meta={
                "manga_name": manga_name,
                "manga_id": manga_id,
                "spider": self,
            },
        )

    def parse_manga_html(self, response):
        """
        Decode compressed HTML from __VIEWSTATE, wrap as HtmlResponse, and parse chapters.
        """
        packed_html = response.css("div input#__VIEWSTATE::attr(value)").get()

        if not packed_html:
            yield from parse_manga_page(response)
            return

        html_string = "".join(LZString().decompressFromBase64(packed_html))

        fake_response = HtmlResponse(
            url=response.url,
            body=html_string,
            encoding="utf-8",
            request=response.request,
        )

        yield from parse_manga_page(fake_response)
