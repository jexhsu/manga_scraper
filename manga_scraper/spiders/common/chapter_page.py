# manga_scraper/spiders/parse_chapter.py
from random import randint, random
from manga_scraper.items import ChapterPageLinkItem, PageItem


async def parse_chapter_page(response):
    chapter_id = response.meta["chapter_id"]
    manga_id = response.meta["manga_id"]
    page_urls = response.css("div[data-name='image-item'] img::attr(src)").getall()

    for idx, url in enumerate(page_urls, start=1):
        yield PageItem(
            manga_id=manga_id,
            chapter_id=chapter_id,
            page_number=idx,
            page_url=url,
        )

        yield ChapterPageLinkItem(
            manga_id=manga_id,
            chapter_id=chapter_id,
            page_id=idx,
            total_pages=len(page_urls),
        )

    if "playwright_page" in response.meta:
        await response.meta["playwright_page"].close()
