# manga_scraper/spiders/common/chapter_page.py
from manga_scraper.items import PageItem, ChapterPageLinkItem
from manga_scraper.utils.decrypt_content_key import decrypt_content_key
from manga_scraper.utils.js_var_extractor import extract_js_var


def parse_chapter_page(response):
    """
    Parse image URLs from chapter AJAX response (JSON format).

    Args:
        response (scrapy.Response): JSON response from chapter endpoint.
    """
    spider = response.meta["spider"]
    manga_id = response.meta["manga_id"]
    manga_name = response.meta["manga_name"]
    chapter_id = response.meta["chapter_id"]
    chapter_group = response.meta["chapter_group"]
    chapter_type = response.meta["chapter_type"]
    chapter_number_name = response.meta["chapter_number_name"]

    config = spider.manga_parser_config["chapter_parser_config"]

    content_key = response.css(config["content_key_selector"]).get()
    aes_key = extract_js_var(response)

    page_objs = decrypt_content_key(content_key, aes_key)

    urls = [p["url"] for p in page_objs if "url" in p]

    page_urls = urls[:1] if spider.debug_mode else urls

    for idx, url in enumerate(page_urls, start=1):
        yield PageItem(
            manga_name=manga_name,
            manga_id=manga_id,
            chapter_name=chapter_number_name,
            chapter_id=chapter_id,
            chapter_group=chapter_group,
            chapter_type=chapter_type,
            page_number=idx,
            page_url=url,
        )

        yield ChapterPageLinkItem(
            manga_id=manga_id,
            chapter_id=chapter_id,
            page_id=idx,
            total_pages=len(page_urls),
        )
