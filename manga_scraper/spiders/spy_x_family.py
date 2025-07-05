# manga_scraper/spiders/spy_x_family.py
import re
from scrapy import Spider
import scrapy
from manga_scraper.spiders.common.config import MangaParserConfig, ChapterParserConfig
from manga_scraper.spiders.common.manga_page import parse_manga_page


class AjinSpider(Spider):
    name = "spy_x_family"
    base_url = "https://mangaspyfamily.com"

    manga_parser_config = MangaParserConfig.create_site_config(
        chapters_selector='div[aria-label="Post Carousel"] article',
        chapter_id_extractor=lambda url: url.split("/")[-2],
        chapter_number_extractor=lambda el: re.search(
            r"(chapter .+)", el.css("a::text").get(), re.IGNORECASE
        ).group(1),
        use_playwright=False,
        chapter_parser_config=ChapterParserConfig.create_site_config(
            page_urls_extractor=lambda response: [
                srcset.split(",")[-1].split()[0]
                for srcset in response.css(
                    "figure figure.wp-block-image noscript img::attr(srcset)"
                ).getall()
            ],
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
