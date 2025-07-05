from scrapy_playwright.page import PageMethod


def setup_playwright(wait_for_selector: str) -> dict:
    """
    Generate Playwright meta settings for chapter pages.
    Returns:
        dict: Meta dictionary for Scrapy Request
    """
    return {
        "playwright": True,
        "playwright_page_methods": [
            PageMethod("wait_for_selector", wait_for_selector, timeout=600000),
            PageMethod("evaluate", "() => { window.stop(); }"),
        ],
        "playwright_page_goto_kwargs": {
            "wait_until": "domcontentloaded",
            "timeout": 600000,
        },
        "playwright_include_page": True,
    }
