# manga_scraper/utils/playwright_setup.py
from scrapy_playwright.page import PageMethod


def setup_playwright_meta(meta, image_selector):
    """
    Setup Playwright metadata for requests.

    Args:
        meta (dict): Existing request metadata.
        image_selector (str): CSS selector for images.

    Returns:
        dict: Updated metadata with Playwright configuration.
    """
    meta.update(
        {
            "playwright": True,
            "playwright_page_methods": [
                PageMethod("wait_for_selector", image_selector),
                PageMethod("wait_for_timeout", 1000),
            ],
            "playwright_page_goto_kwargs": {"wait_until": "domcontentloaded"},
            "playwright_include_page": True,
        }
    )
    return meta
