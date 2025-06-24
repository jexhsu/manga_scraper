# manga_scraper/spiders/parse_chapter.py
from manga_scraper.items import ChapterPageLinkItem, MangaChapterLinkItem, PageItem


async def parse_chapter_page(response):
    page_urls = response.css("div[data-name='image-item'] img::attr(src)").getall()[:2]
    chapter_id = response.meta["chapter_id"]
    manga_id = response.meta["manga_id"]

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
