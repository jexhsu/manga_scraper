# manga_scraper/spiders/manga_park.py
from urllib.parse import urljoin, quote
from manga_scraper.items import ChapterItem, MangaItem, PageItem
import scrapy
from scrapy_playwright.page import PageMethod


class MangaParkSpider(scrapy.Spider):
    name = "manga_park"
    allowed_domains = ["mangapark.io"]

    def __init__(self, search_term="attack on titan", **kwargs):
        super().__init__(**kwargs)
        self.search_term = search_term

    def start_requests(self):
        url = f"https://mangapark.io/search?word={quote(self.search_term)}"
        yield scrapy.Request(url, self.parse_search_page)

    def parse_search_page(self, response):
        manga = response.css("div.flex.border-b.border-b-base-200.pb-5")[0]
        manga_url = manga.css("h3 a::attr(href)").get()
        yield MangaItem(
            manga_name=manga.css('span[q\\:key="Ts_1"]')
            .xpath("string(.)")
            .get()
            .strip(),
            manga_url=manga_url,
        )
        yield scrapy.Request(urljoin(response.url, manga_url), self.parse_manga_page)

    def parse_manga_page(self, response):
        chapter = response.css("div[data-name='chapter-list'] [q\\:key='8t_8']")[-1]
        yield ChapterItem(
            chapter_url=chapter.css("a::attr(href)").get(),
            chapter_number_name=chapter.css("a::text").get(),
            chapter_text_name=chapter.css("span[q\\:key='8t_1']::text").get(),
        )
        yield scrapy.Request(
            urljoin(response.url, chapter.css("a::attr(href)").get()),
            callback=self.parse_chapter_page,
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod(
                        "wait_for_selector",
                        "div[data-name='image-item']",
                        timeout=600000,
                    )
                ],
                "playwright_page_goto_kwargs": {
                    "wait_until": "domcontentloaded",
                    "timeout": 600000,
                },
            },
        )

    def parse_chapter_page(self, response):
        page_urls = response.css("div[data-name='image-item'] img::attr(src)").getall()
        yield from (PageItem(page_url=url) for url in page_urls)
