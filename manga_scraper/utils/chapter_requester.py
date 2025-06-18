# manga_scraper/utils/chapter_requester.py
import scrapy
import os
import logging
from manga_scraper.utils.playwright_setup import setup_playwright_meta
from manga_scraper.utils.file_manager import remove_folder


def request_next_chapter(spider, chapter_map):
    """
    Handles chapter requests with retry mechanism

    Args:
        spider: Scrapy spider instance
        chapter_map: Dictionary containing chapter data with format {chapter_key: chapter_value}

    Yields:
        scrapy.Request: Request for the next chapter or retry attempt
    """
    # Get current chapter details from the chapter map
    chapter_val = list(chapter_map.values())[spider.chapter_index]
    current_key = list(chapter_map.keys())[spider.chapter_index]

    # Retry Logic - Handle failed chapter requests
    if not spider.chapter_completed_map.get(current_key):
        # Check if retry attempts remain
        if spider.current_retry < spider.max_retries:
            # Increment retry counter
            spider.current_retry += 1

            # Print retry status to console (visible in all log levels)
            print(
                f"\n🔄 Retrying chapter {current_key} (attempt {spider.current_retry}/{spider.max_retries})"
            )

            # Log retry status for debugging purposes
            logging.debug(
                f"\n🔄 Retrying chapter {current_key} (attempt {spider.current_retry}/{spider.max_retries})"
            )

            # Setup metadata for the retry request
            meta = {"chapter": current_key, "retry_count": spider.current_retry}

            # Configure Playwright if enabled for the spider
            if getattr(spider, "use_playwright", False):
                meta = setup_playwright_meta(meta, spider.image_selector)
                logging.debug("Playwright meta setup for retry: %s", meta)

            # Create retry request with increased priority for subsequent attempts
            yield scrapy.Request(
                url=spider.url_template.format(chapter=chapter_val),
                callback=spider.parse_chapter,
                meta=meta,
                dont_filter=True,  # Allow retrying the same URL
                priority=spider.current_retry * 10,  # Higher priority for later retries
            )
            return
        else:
            # All retry attempts exhausted
            print(
                f"❌ Failed chapter {current_key} after {spider.max_retries} attempts"
            )

            logging.debug(
                f"❌ Failed chapter {current_key} after {spider.max_retries} attempts"
            )

            # Mark chapter as failed and reset retry counter
            spider.current_retry = 0
            spider.chapter_completed_map[current_key] = False

    # Chapter Advancement - Move to next chapter if current is completed/failed
    while spider.chapter_index + 1 < len(chapter_map):
        # Increment to next chapter
        spider.chapter_index += 1
        chapter = list(chapter_map.values())[spider.chapter_index]
        chapter_key = list(chapter_map.keys())[spider.chapter_index]

        # Check if chapter was previously completed but needs redownload
        if spider.chapter_completed_map.get(chapter_key, False):
            # Remove existing chapter folder to prepare for redownload
            folder = os.path.join(
                spider.root_dir, spider.site_name, f"chapter-{chapter_key}"
            )
            remove_folder(folder)
            logging.debug("Removed existing folder for chapter %s", chapter_key)
            continue

        # Reset retry counter for new chapter
        spider.current_retry = 0

        # Print status for new chapter request
        print(f"📖 Moving to chapter {chapter_key}")

        logging.debug("📖 Moving to chapter %s", chapter_key)

        # Setup metadata for new chapter request
        meta = {"chapter": chapter_key, "retry_count": 0}

        # Configure Playwright if enabled
        if getattr(spider, "use_playwright", False):
            meta = setup_playwright_meta(meta, spider.image_selector)
            logging.debug("Playwright meta setup for new chapter: %s", meta)

        # Create request for next chapter
        yield scrapy.Request(
            url=spider.url_template.format(chapter=chapter),
            callback=spider.parse_chapter,
            meta=meta,
        )
        break
