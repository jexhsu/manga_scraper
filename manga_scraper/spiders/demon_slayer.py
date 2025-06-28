# manga_scraper/spiders/manga_park.py
import re
from urllib.parse import urljoin
from scrapy import Spider
import scrapy
from scrapy_playwright.page import PageMethod
from scrapy.http import HtmlResponse
from manga_scraper.spiders.common.chapter_page import parse_chapter_page
from manga_scraper.spiders.common.config import ChapterParserConfig, MangaParserConfig
from manga_scraper.spiders.common.manga_page import parse_manga_page


class DemonSlayerSpider(Spider):
    name = "demon_slayer"
    base_url = "https://www.demonslayerr.com"

    manga_parser_config = MangaParserConfig.create_site_config(
        chapters_selector="div.card",
        chapter_id_extractor=lambda url: url.split("/")[-1],
        chapter_number_extractor=lambda el: re.search(
            r"(chapter .+)", el.css("strong::text").get(), re.IGNORECASE
        ).group(1),
        chapter_text_extractor=lambda el: el.css("a.h5::text").get(),
        use_playwright_meta=False,
        chapter_parser_config=ChapterParserConfig.create_site_config(
            page_urls_selector="div img.w-100::attr(src)",
            async_cleanup=False,
        ),
    )

    def start_requests(self):
        url = f"{self.base_url}/demon-slayer/manga/chapters"
        yield scrapy.Request(
            url,
            callback=self.parse_load_more_button,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "div.card")
                ],
            },
        )

    async def parse_load_more_button(self, response):
        page = response.meta["playwright_page"]

        for _ in range(30):
            button = await page.query_selector(
                "button.btn.bg-gradient-primary.icon-move-down:not([disabled])"
            )
            if not button:
                break

            await button.click()
            await page.wait_for_timeout(1500)

        content = await page.content()
        await page.close()

        selector = scrapy.Selector(text=content)

        fake_response = HtmlResponse(
            url=response.url,
            body=content,
            encoding="utf-8",
            request=response.request,
        )
        fake_response.meta["manga_id"] = self.name
        fake_response.meta["spider"] = self

        for item in parse_manga_page(fake_response, selector):
            yield item
