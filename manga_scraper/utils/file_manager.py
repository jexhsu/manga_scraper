import os
import shutil
import logging


def create_download_folder(root_dir, site_name, chapter):
    """Create a folder for the chapter if it doesn't exist."""
    folder = os.path.join(root_dir, site_name, f"chapter-{chapter}")
    os.makedirs(folder, exist_ok=True)
    return folder


def check_all_images_exist(folder, img_urls):
    total = len(img_urls)
    missing_files = []
    downloaded_count = 0

    for index in range(total):
        ext = os.path.splitext(img_urls[index])[1].split("?")[0].lower()
        filename = f"{index + 1:03d}{ext}"
        path = os.path.join(folder, filename)
        if os.path.exists(path):
            downloaded_count += 1
        else:
            missing_files.append(filename)

    all_exist = downloaded_count == total
    return {
        "all_exist": all_exist,
        "downloaded_count": downloaded_count,
    }


def remove_folder(folder):
    """Remove the folder if it exists."""
    if os.path.exists(folder):
        shutil.rmtree(folder)
        logging.debug(f"🗑️ Removed folder: {folder}")
