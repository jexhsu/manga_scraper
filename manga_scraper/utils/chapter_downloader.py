import os
import shutil
import logging
from manga_scraper.utils.file_manager import (
    check_all_images_exist,
    create_download_folder,
    remove_folder,
)


def prepare_chapter_download(
    root_dir, site_name, chapter, img_urls=[], progress_bar=None, use_playwright=False
):
    """
    Prepare the download folder and determine whether to skip this chapter.
    Return (skip: bool, folder_path: str, scrapy.Request or None)
    """
    logging.debug("Preparing download for chapter %s (site: %s)", chapter, site_name)
    logging.debug("Parameters - root_dir: %s, img_urls count: %d, use_playwright: %s", 
                 root_dir, len(img_urls), use_playwright)

    if not use_playwright:
        total = len(img_urls)
        if total == 0:
            logging.debug("No images found for chapter %s, skipping", chapter)
            print(f"\n⚠️ Chapter {chapter}: No images found, skipping.\n")
            return True, None, None

    folder = create_download_folder(root_dir, site_name, chapter)
    pdf_path = os.path.join(os.path.dirname(folder), f"chapter-{chapter}.pdf")
    logging.debug("Created download folder: %s", folder)
    logging.debug("PDF path: %s", pdf_path)

    # Step 1: PDF exists? Skip chapter
    if os.path.exists(pdf_path) and not img_urls:
        logging.debug("PDF already exists for chapter %s, skipping", chapter)
        print(f"\n✅ Chapter {chapter}: This chapter has already been downloaded. Skipping...")
        remove_folder(folder)
        return True, None, None

    if use_playwright:
        logging.debug("Playwright mode enabled, returning basic info")
        return False, folder, None

    # Step 2: Check image existence and get details
    logging.debug("Checking existing images in folder %s", folder)
    check_result = check_all_images_exist(folder, img_urls)
    all_exist = check_result["all_exist"]
    downloaded = check_result["downloaded_count"]
    logging.debug("Image check result - all_exist: %s, downloaded_count: %d", all_exist, downloaded)

    if all_exist:
        logging.debug("All images exist for chapter %s, skipping download", chapter)
        print(f"\n✅ Chapter {chapter}: All images already downloaded, skipping download.")
        remove_folder(folder)
        return True, None, None

    # Step 3: Some images missing, prepare to download remaining
    if downloaded:
        logging.debug("Partial download found (%d/%d images)", downloaded, total)
        print(f"\n📥 Chapter {chapter}: Downloading images. {downloaded}/{total} already downloaded.")
    elif img_urls:
        logging.debug("Starting fresh download for %d images", total)
        print(f"\n📥 Chapter {chapter}: Starting fresh download of {total} images...")

    if progress_bar:
        progress_bar.last_progress_length = 0
        logging.debug("Reset progress bar for new download")

    meta_info = {
        "chapter": chapter,
        "img_urls": img_urls,
        "index": downloaded,  # start from first missing image
        "folder": folder,
        "total": total,
        "downloaded": downloaded,
    }
    logging.debug("Prepared download meta info: %s", meta_info)
    
    return (False, folder, meta_info)