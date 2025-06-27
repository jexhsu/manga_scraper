from urllib.parse import urljoin, quote
import scrapy
from manga_scraper.items import (
    MangaItem,
    SearchKeywordMangaLinkItem,
)
from manga_scraper.settings import BASE_URL
from .common.manga_page import parse_manga_page
from .common.chapter_page import parse_chapter_page  # Add this import
from manga_scraper.utils.playwright_config import get_chapter_page_meta


class MangaParkSpider(scrapy.Spider):
    name = "manga_park"

    def __init__(
        self,
        search_term=None,
        mode="search_all",
        manga_id=None,
        chapter_ids=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.mode = mode  # search_all | search_only | chapters_only | chapters_select
        self.search_term = search_term
        self.manga_id = manga_id
        self.chapter_ids = chapter_ids.split(",") if chapter_ids else []

    def start_requests(self):
        # Mode: search_all → crawl full manga + chapters + images
        # Mode: search_only → only fetch search results (manga list)
        if self.mode in ["search_all", "search_only"] and self.search_term:
            url = (
                f"{BASE_URL}/search?word={quote(self.search_term)}&sortby=field_follow"
            )
            yield scrapy.Request(url, callback=self.parse_search_page)

        # Mode: chapters_only → fetch all chapters for a manga
        # Mode: chapters_select → fetch selected chapters only
        elif self.mode in ["chapters_only", "chapters_select"] and self.manga_id:
            url = f"{BASE_URL}/comic/{self.manga_id}"
            yield scrapy.Request(
                url,
                callback=self.parse_chapters_for_manga,
                meta={"manga_id": self.manga_id},
            )
        else:
            self.logger.error("Missing required parameters.")

    def parse_search_page(self, response):
        manga_list = response.css("div.flex.border-b.border-b-base-200.pb-5")
        for manga in manga_list:
            manga_url = manga.css("h3 a::attr(href)").get()
            manga_id = manga_url.split("/")[-1]

            yield MangaItem(  # Store basic manga info
                manga_name=manga.css('span[q\\:key="Ts_1"]')
                .xpath("string(.)")
                .get()
                .strip(),
                manga_url=manga_url,
                manga_id=manga_id,
                manga_follows=manga.css(
                    'div[id^="comic-follow-swap-"] span::text'
                ).get(),
            )
            yield SearchKeywordMangaLinkItem(
                keyword=self.search_term,
                manga_id=manga_id,
                total_mangas=len(manga_list),
            )

            # Only follow manga page if mode is search_all
            if self.mode == "search_all":
                yield scrapy.Request(
                    urljoin(response.url, manga_url),
                    callback=parse_manga_page,
                    meta={"manga_id": manga_id, "follow_chapters": True},
                )

    def parse_chapters_for_manga(self, response):
        """
        Called when mode is chapters_only or chapters_select.
        """
        manga_id = response.meta["manga_id"]
        chapters = response.css("div[data-name='chapter-list'] [q\\:key='8t_8']")

        for chapter in chapters:
            chapter_url = chapter.css("a::attr(href)").get()
            chapter_id = chapter_url.split("/")[-1]

            if self.mode == "chapters_select" and chapter_id not in self.chapter_ids:
                continue  # skip chapters not in selected list

            yield response.follow(
                chapter_url,
                callback=parse_chapter_page,
                meta=get_chapter_page_meta(manga_id=manga_id, chapter_id=chapter_id),
            )
