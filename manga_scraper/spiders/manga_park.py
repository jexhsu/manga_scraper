# manga_scraper/spiders/manga_park.py
from urllib.parse import quote, urljoin

import scrapy
from manga_scraper.items import MangaItem, SearchKeywordMangaLinkItem
from manga_scraper.spiders import BaseMangaSpider
from manga_scraper.spiders.common.config import ChapterParserConfig, MangaParserConfig
from .common.manga_page import parse_manga_page
from manga_scraper.utils.search_filter import select_manga_interactively
from manga_scraper.spiders import BaseMangaSpider


class MangaParkSpider(BaseMangaSpider):
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
        use_playwright=True,
        chapter_parser_config=ChapterParserConfig.create_site_config(
            page_urls_selector="div[data-name='image-item'] img::attr(src)",
            async_cleanup=True,
        ),
    )

    def start_requests(self):
        url = (
            f"{self.base_url}/search?word={quote(self.search_term)}&sortby=field_follow"
        )
        yield scrapy.Request(url, callback=self.parse_search_page)

    def parse_search_page(self, response):

        search_items = response.css("div.flex.border-b.border-b-base-200.pb-5")

        selected = select_manga_interactively(
            search_items,
            manga_name_extractor=lambda el: el.css('span[q\\:key="Ts_1"]')
            .xpath("string(.)")
            .get()
            .strip(),
            debug_choice=0 if self.debug_mode else None,
        )

        manga_name = (
            selected.css('span[q\\:key="Ts_1"]').xpath("string(.)").get().strip()
        )
        manga_url = selected.css("h3 a::attr(href)").get()
        manga_id = manga_url.split("/")[-1]
        manga_follows = selected.css('div[id^="comic-follow-swap-"] span::text').get()

        yield MangaItem(
            manga_name=manga_name,
            manga_url=manga_url,
            manga_id=manga_id,
            manga_follows=manga_follows,
        )

        yield SearchKeywordMangaLinkItem(
            keyword=self.search_term,
            manga_id=manga_id,
            total_mangas=len(search_items),
        )

        yield scrapy.Request(
            urljoin(self.base_url, manga_url),
            callback=parse_manga_page,
            meta={
                "manga_id": manga_id,
                "spider": self,
            },
        )
