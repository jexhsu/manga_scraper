# manga_scraper/spiders/manga_park.py
from typing import Dict
from urllib.parse import quote, urljoin
from manga_scraper.items import MangaItem, SearchKeywordMangaLinkItem
import scrapy
from manga_scraper.spiders.common.config import ChapterParserConfig, MangaParserConfig
from .common.manga_page import parse_manga_page


class MangaParkSpider(scrapy.Spider):
    name = "manga_park"
    base_url = "https://mangapark.io"

    custom_settings = {
        "DEPTH_LIMIT": 3,
        "CLOSESPIDER_PAGECOUNT": 100,
    }

    manga_parser_config = MangaParserConfig.create_site_config(
        chapters_selector="div[data-name='chapter-list'] [q\\:key='8t_8']",
        chapter_id_extractor=lambda url: url.split("/")[-1],
        chapter_number_extractor=lambda el: el.css("a::text").get(),
        chapter_text_extractor=lambda el: el.css("span[q\\:key='8t_1']::text").get(),
        use_playwright_meta=True,
        chapter_parser_config=ChapterParserConfig.create_site_config(
            page_urls_selector="div[data-name='image-item'] img::attr(src)",
            async_cleanup=True,
        ),
    )

    def __init__(self, search_term="a girl on the shore", **kwargs):
        super().__init__(**kwargs)
        self.search_term = search_term

    def start_requests(self):
        url = (
            f"{self.base_url}/search?word={quote(self.search_term)}&sortby=field_follow"
        )
        yield scrapy.Request(url, callback=self.parse_search_page)

    def parse_search_page(self, response):
        manga_list = response.css("div.flex.border-b.border-b-base-200.pb-5")[:1]

        for manga in manga_list:
            manga_url = manga.css("h3 a::attr(href)").get()
            manga_id = manga_url.split("/")[-1]
            manga_follows = manga.css('div[id^="comic-follow-swap-"] span::text').get()
            yield MangaItem(
                manga_name=manga.css('span[q\\:key="Ts_1"]')
                .xpath("string(.)")
                .get()
                .strip(),
                manga_url=manga_url,
                manga_id=manga_id,
                manga_follows=manga_follows,
            )
            yield SearchKeywordMangaLinkItem(
                keyword=self.search_term,
                manga_id=manga_id,
                total_mangas=len(manga_list),
            )
            yield scrapy.Request(
                urljoin(response.url, manga_url),
                callback=parse_manga_page,
                meta={
                    "manga_id": manga_id,
                    "spider": self,
                },
            )
