# manga_scraper/spiders/tokyo_ghoul.py
import re
from scrapy import Spider
import scrapy
from manga_scraper.spiders.common.config import MangaParserConfig, ChapterParserConfig
from manga_scraper.spiders.common.manga_page import parse_manga_page


class TokyoGhoulSpider(Spider):
    name = "tokyo_ghoul"
    base_url = "https://tgmanga.com"

    manga_parser_config = MangaParserConfig.create_site_config(
        chapters_selector="li#ceo_latest_comics_widget-3 ul li",
        chapter_id_extractor=lambda url: url.split("/")[-2],
        chapter_number_extractor=lambda el: re.search(
            r"(chapter .+)", el.css("a::text").get(), re.IGNORECASE
        ).group(1),
        use_playwright_meta=False,
        chapter_parser_config=ChapterParserConfig.create_site_config(
            page_urls_selector="div.entry-content div.separator img::attr(src), p img[decoding='async']::attr(src)",
            async_cleanup=False,
        ),
    )

    def start_requests(self):
        url = self.base_url
        yield scrapy.Request(
            url,
            callback=parse_manga_page,
            meta={
                "manga_id": self.name,
                "spider": self,  # Pass spider instance
            },
        )
