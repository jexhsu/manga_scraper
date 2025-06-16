import scrapy
import logging
from scrapy_playwright.page import PageMethod
from manga_scraper.utils.chapter_downloader import prepare_chapter_download

def request_next_chapter(spider, chapter_list_or_map):
    """
    Issue a Scrapy request for the next chapter.
    """
    chapters = list(chapter_list_or_map.values()) if isinstance(chapter_list_or_map, dict) else chapter_list_or_map
    
    spider.chapter_index += 1

    if spider.chapter_index < len(chapters):
        next_chapter = chapters[spider.chapter_index]

        if spider.use_playwright:
            result = prepare_chapter_download(spider.root_dir, spider.site_name, spider.chapter_index, use_playwright=True)
            skip = result[0]
            if skip:
                for req in request_next_chapter(spider, spider.chapter_map):
                    yield req

        meta = {'chapter': spider.chapter_index}

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
