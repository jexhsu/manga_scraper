# manga_scraper/utils/image_url_extractor.py
import logging
from scrapy.http import Response


async def extract_image_urls(response: Response, spider) -> list:
    """
    Asynchronously extract image URLs from the response.

    Handles both Playwright-rendered pages and regular Scrapy responses.

    Args:
        response (scrapy.http.Response): The response object.
        spider (scrapy.Spider): The spider instance for configuration.

    Returns:
        list: List of extracted image URLs.
    """
    if "playwright_page" in response.meta:
        page = response.meta["playwright_page"]
        await page.wait_for_selector(spider.image_selector)
        img_elements = await page.query_selector_all(spider.image_selector)
        img_urls = [await el.get_attribute("src") for el in img_elements]
        logging.debug(f"Extracted {len(img_urls)} image URLs using Playwright.")
        return page, img_urls
    else:
        img_urls = response.css(f"{spider.image_selector}::attr(src)").getall()
        logging.debug(f"Extracted {len(img_urls)} image URLs using Scrapy.")
        return None, img_urls
