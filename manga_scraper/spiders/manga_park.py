# manga_scraper/spiders/manga_park.py
from urllib.parse import urljoin, quote
from manga_scraper.items import MangaItem, SearchKeywordMangaLinkItem
import scrapy
from manga_scraper.settings import BASE_URL
from .common.manga_page import parse_manga_page


class MangaParkSpider(scrapy.Spider):
    name = "manga_park"

    custom_settings = {
        "DEPTH_LIMIT": 3,
        "CLOSESPIDER_PAGECOUNT": 100,
    }

    def __init__(self, search_term="attack on titan", **kwargs):
        super().__init__(**kwargs)
        self.search_term = search_term

    def start_requests(self):
        url = f"{BASE_URL}/search?word={quote(self.search_term)}"
        yield scrapy.Request(url, callback=self.parse_search_page)

    def parse_search_page(self, response):
        manga_list = response.css("div.flex.border-b.border-b-base-200.pb-5")[:1]

        for manga in manga_list:
            manga_url = manga.css("h3 a::attr(href)").get()
            manga_id = manga_url.split("/")[-1]
            manga_follows = (
                manga.css('div[id^="comic-follow-swap-"] span::text').get(),
            )
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
                meta={"manga_id": manga_id},
            )
