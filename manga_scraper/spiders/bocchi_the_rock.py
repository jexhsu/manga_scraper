# manga_scraper/spiders/bocchi_the_rock.py
import re
import scrapy
from manga_scraper.spiders.common.config import MangaParserConfig, ChapterParserConfig
from manga_scraper.spiders.common.manga_page import parse_manga_page
from manga_scraper.spiders import BaseMangaSpider


class BocchitheRockSpider(BaseMangaSpider):
    name = "bocchi_the_rock"
    base_url = "https://w3.bocchitherockmanga.com"

    manga_parser_config = MangaParserConfig.create_site_config(
        chapters_selector="li#recent-posts-3 ul li",
        chapter_id_extractor=lambda url: url.split("/")[-2],
        chapter_number_extractor=lambda el: re.search(
            r"(chapter .+)", el.css("a::text").get(), re.IGNORECASE
        ).group(1),
        use_playwright=False,
        chapter_parser_config=ChapterParserConfig.create_site_config(
            page_urls_selector="div.separator img::attr(src), figure.wp-block-image img::attr(src)",
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
