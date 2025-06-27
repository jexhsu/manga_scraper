from scrapy_playwright.page import PageMethod


def get_chapter_page_meta(manga_id: str, chapter_id: str) -> dict:
    """
    Generate Playwright meta settings for chapter pages.

    Args:
        manga_id (str): Manga ID
        chapter_id (str): Chapter ID

    Returns:
        dict: Meta dictionary for Scrapy Request
    """
    return {
        "playwright": True,
        "playwright_page_methods": [
            PageMethod(
                "wait_for_selector", "div[data-name='image-item']", timeout=600000
            ),
            PageMethod("evaluate", "() => { window.stop(); }"),
        ],
        "playwright_page_goto_kwargs": {
            "wait_until": "domcontentloaded",
            "timeout": 600000,
        },
        "playwright_include_page": True,
        "manga_id": manga_id,
        "chapter_id": chapter_id,
    }
