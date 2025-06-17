import logging
import scrapy
from manga_scraper.utils.chapter_downloader import prepare_chapter_download
from manga_scraper.utils.chapter_requester import request_next_chapter
from manga_scraper.utils.pdf_converter import convert_chapter_to_pdf
from manga_scraper.utils.download_manager import download_and_save_image
from manga_scraper.utils.error_handling import retry_on_failure

MAX_RETRIES = 5  # max retry attempts per chapter

@retry_on_failure(max_retries=MAX_RETRIES)
async def async_retry_chapter_download(spider, response, img_urls, chapter, folder, meta):
    """
    Retry logic for Playwright async image downloading of a chapter.
    """
    retry_count = meta.get('retry_count', 0)
    if retry_count >= MAX_RETRIES:
        logging.error(f"❌ Chapter {chapter} reached max retry attempts ({retry_count}). Skipping...")
        # Mark chapter as failed/completed if needed
        spider.chapter_completed_map[chapter] = False
        # Request next chapter
        for req in request_next_chapter(spider, spider.chapter_map):
            yield req
        return

    logging.debug(f"🔁 Retrying chapter {chapter}, attempt {retry_count + 1}/{MAX_RETRIES} ...")

    start_index = meta.get("index", 0) or 0
    page = response.meta.get("playwright_page")
    for index in range(start_index, len(img_urls)):
        img_url = img_urls[index]
        success = await download_and_save_image(page, img_url, index, folder, spider.use_playwright)
        if not success:
            # Retry this chapter again
            meta['retry_count'] = retry_count + 1
            for req in async_retry_chapter_download(spider, response, img_urls, chapter, folder, meta):
                yield req
            return
        progress_text = f"⏳ Chapter {chapter}: {spider.progress_bar.progress_bar(index + 1, len(img_urls))} ({index + 1}/{len(img_urls)}) "
        spider.progress_bar.update_progress(progress_text)

    spider.progress_bar.clear_progress()
    logging.info(f"✅ Chapter {chapter}: Download completed!")
    spider.chapter_completed_map[chapter] = True
    convert_chapter_to_pdf(folder)
    for req in request_next_chapter(spider, spider.chapter_map):
        yield req
    return

@retry_on_failure(max_retries=MAX_RETRIES)
def sync_retry_chapter_download(spider, response):
    """
    Retry logic for synchronous Scrapy image downloading of a chapter.
    It retries the whole chapter if any image fails.
    """
    meta = response.meta
    chapter = meta['chapter']
    retry_count = meta.get('retry_count', 0)

    if retry_count >= MAX_RETRIES:
        logging.error(f"❌ Chapter {chapter} reached max retry attempts ({retry_count}). Skipping...")
        spider.chapter_completed_map[chapter] = False
        yield from request_next_chapter(spider, spider.chapter_list)
        return

    img_urls = meta['img_urls']
    index = meta['index']
    folder = meta['folder']
    total = meta['total']
    downloaded = meta.get('downloaded', 0) + 1

    success = download_and_save_image(response, img_urls, index, folder, spider.use_playwright)
    if not success:
        # Retry chapter from scratch
        logging.debug(f"🔁 Retrying chapter {chapter}, attempt {retry_count + 1}/{MAX_RETRIES} ...")
        meta['retry_count'] = retry_count + 1
        # Re-start from first image
        meta['index'] = 0
        meta['downloaded'] = 0
        yield scrapy.Request(
            url=img_urls[0],
            callback=spider.download_image,
            errback=spider.handle_error,
            meta=meta,
            dont_filter=True
        )
        return

    progress_text = f"⏳ Chapter {chapter}: {spider.progress_bar.progress_bar(downloaded, total)} ({downloaded}/{total}) "
    spider.progress_bar.update_progress(progress_text)

    if index + 1 < total:
        yield scrapy.Request(
            url=img_urls[index + 1],
            callback=spider.download_image,
            errback=spider.handle_error,
            meta={
                'chapter': chapter,
                'img_urls': img_urls,
                'index': index + 1,
                'folder': folder,
                'total': total,
                'downloaded': downloaded,
                'retry_count': retry_count,
            },
            dont_filter=True
        )
    else:
        spider.progress_bar.clear_progress()
        logging.info(f"✅ Chapter {chapter}: Download completed!")
        spider.chapter_completed_map[chapter] = True
        convert_chapter_to_pdf(folder)
        yield from request_next_chapter(spider, spider.chapter_list)
