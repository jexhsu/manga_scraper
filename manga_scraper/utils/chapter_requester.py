import scrapy
import logging
from scrapy_playwright.page import PageMethod

def request_next_chapter(spider, response=None):
    """
    Issue a Scrapy request for the next chapter.
    """
    spider.chapter_index += 1

    if spider.chapter_index < len(spider.chapter_list):
        next_chapter = spider.chapter_list[spider.chapter_index]

        meta = {'chapter': next_chapter}

        if getattr(spider, 'use_playwright', False):
            meta.update({
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", spider.image_selector),
                    PageMethod("wait_for_timeout", 1000),
                ],
                "playwright_page_goto_kwargs": {"wait_until": "domcontentloaded"},
                "playwright_include_page": True,
            })

        yield scrapy.Request(
            url=spider.url_template.format(chapter=next_chapter),
            callback=spider.parse_chapter,
            meta=meta,
            errback=spider.handle_error
        )
    else:
        logging.info("🎉 All chapters downloaded and converted!")
