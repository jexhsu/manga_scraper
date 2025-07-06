# manga_scraper/spiders/Weeb_Centra.py
import scrapy
from urllib.parse import urljoin
from manga_scraper.items import MangaItem, SearchKeywordMangaLinkItem
from manga_scraper.spiders.common.config import ChapterParserConfig, MangaParserConfig
from manga_scraper.spiders.common.manga_page import parse_manga_page
from manga_scraper.utils.search_filter import select_manga_interactively


class WeebCentralSpider(scrapy.Spider):
    name = "weeb_central"
    base_url = "https://weebcentral.com"

    # Placeholders for future use
    manga_parser_config = MangaParserConfig.create_site_config(
        chapters_selector='div a[class*="hover:bg-base-300"]',
        chapter_id_extractor=lambda el: el.css("a::attr(href)").get().split("/")[-1],
        chapter_number_extractor=lambda el: el.css("span.grow span::text")
        .get()
        .strip(),
        chapter_parser_config=ChapterParserConfig.create_site_config(
            page_urls_selector="section img::attr(src)",  # Define if needed later
            async_cleanup=False,
        ),
        use_playwright=False,
    )

    def __init__(self, search_term="a girl on the shore", **kwargs):
        super().__init__(**kwargs)
        self.search_term = search_term

    def start_requests(self):

        formdata = {"text": self.search_term}
        yield scrapy.FormRequest(
            url=f"{self.base_url}/search/simple?location=main",
            method="POST",
            formdata=formdata,
            callback=self.parse_search_preview,
        )

    def parse_search_preview(self, response):

        search_items = response.css("div[x-show='showResult'] a")

        selected = select_manga_interactively(
            search_items,
            manga_name_extractor=lambda el: el.css("div.text-left::text").get(),
        )

        manga_name = selected.css("div.text-left::text").get().strip()
        manga_url = urljoin(self.base_url, selected.attrib.get("href"))
        manga_id = manga_url.split("/")[-2]

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
            url=f"{self.base_url}/series/{manga_id}/full-chapter-list",
            callback=parse_manga_page,
            meta={"manga_name": manga_name, "manga_id": manga_id, "spider": self},
        )
