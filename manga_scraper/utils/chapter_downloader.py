import os
import shutil
from manga_scraper.utils.file_manager import (
    check_all_images_exist,
    create_download_folder,
    remove_folder
)

def prepare_chapter_download(root_dir, site_name, chapter, img_urls=[], progress_bar=None, use_playwright=False):
    """
    Prepare the download folder and determine whether to skip this chapter.
    Return (skip: bool, folder_path: str, scrapy.Request or None)
    """
    if not use_playwright:
        total = len(img_urls)
        if total == 0:
            print(f"\n⚠️ Chapter {chapter}: No images found, skipping.\n")
            return True, None, None
    
    folder = create_download_folder(root_dir, site_name, chapter)
    pdf_path = os.path.join(os.path.dirname(folder), f"chapter-{chapter}.pdf")

    # Step 1: PDF exists? Skip chapter
    if os.path.exists(pdf_path) and not img_urls:
        print(f"\n✅ Chapter {chapter}: This chapter has already been downloaded. Skipping...")
        remove_folder(folder)
        return True, None, None
    
    if use_playwright:
        return False, folder, None

    # Step 2: Check image existence and get details
    check_result = check_all_images_exist(folder, img_urls)
    all_exist = check_result['all_exist']
    downloaded = check_result['downloaded_count']

    if all_exist:
        print(f"\n✅ Chapter {chapter}: All images already downloaded, skipping download.")
        remove_folder(folder)
        return True, None, None
    
    # Step 3: Some images missing, prepare to download remaining
    if downloaded:
        print(f"\n📥 Chapter {chapter}: Downloading images. {downloaded}/{total} already downloaded.")
    elif img_urls:
        print(f"\n📥 Chapter {chapter}: Starting fresh download of {total} images...")

    progress_bar.last_progress_length = 0
    return False, folder, {
        'chapter': chapter,
        'img_urls': img_urls,
        'index': downloaded,  # start from first missing image
        'folder': folder,
        'total': total,
        'downloaded': downloaded
    }
