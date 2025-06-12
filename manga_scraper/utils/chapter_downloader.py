from manga_scraper.utils.file_manager import (
    create_download_folder,
    check_existing_downloads,
    remove_folder
)

def prepare_chapter_download(root_dir, site_name, chapter, img_urls, file_ext, progress_bar):
    """
    Prepare download folder and determine whether to skip this chapter.
    Return (skip: bool, folder_path: str, scrapy.Request or None)
    """
    total = len(img_urls)
    if total == 0:
        print(f"\n⚠️ Chapter {chapter}: No images found, skipping.\n")
        return True, None, None

    folder = create_download_folder(root_dir, site_name, chapter)

    if check_existing_downloads(folder, file_ext):
        print(f"\n✅ Chapter {chapter}: Already downloaded, skip.")
        remove_folder(folder)
        return True, None, None

    print(f"\n📥 Chapter {chapter}: Downloading {total} images...")
    progress_bar.last_progress_length = 0

    return False, folder, {
        'chapter': chapter,
        'img_urls': img_urls,
        'index': 0,
        'folder': folder,
        'total': total,
        'downloaded': 0
    }
