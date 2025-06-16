import scrapy
import os
import logging
from scrapy_playwright.page import PageMethod
from manga_scraper.utils.file_manager import remove_folder

def request_next_chapter(spider, chapter_source):
    """
    Generate the next chapter request, skipping completed chapters and cleaning up their folders.
    """
    chapters = list(chapter_source.values()) if isinstance(chapter_source, dict) else chapter_source

    while spider.chapter_index + 1 < len(chapters):
        spider.chapter_index += 1
        chapter = chapters[spider.chapter_index]
        key = list(chapter_source.keys())[spider.chapter_index] if isinstance(chapter_source, dict) else chapter

        if spider.chapter_completed_map.get(key):
            print(f"\n✅ Chapter {key}: This chapter has already been downloaded. Skipping...")
            folder = os.path.join(spider.root_dir, spider.site_name, f"chapter-{key}")
            remove_folder(folder)
            continue

        meta = {'chapter': key}
        if getattr(spider, 'use_playwright', False):
            meta.update({
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_goto_kwargs": {"wait_until": "domcontentloaded"},
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", spider.image_selector),
                    PageMethod("wait_for_timeout", 1000),
                ],
            })

        yield scrapy.Request(
            url=spider.url_template.format(chapter=chapter),
            callback=spider.parse_chapter,
            meta=meta,
            errback=spider.handle_error
        )
        break  # Only issue one request
    else:
        logging.info("🎉 All chapters downloaded and converted!")
