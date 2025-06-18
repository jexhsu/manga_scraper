# manga_scraper/utils/pdf_converter.py
import os
from PIL import Image
import img2pdf
import shutil
import logging
from manga_scraper.utils.pdf_utils import get_pdf_output_path


def convert_chapter_to_pdf(chapter_path):
    output_file = get_pdf_output_path(chapter_path)
    logging.debug(f"Starting PDF conversion for: {chapter_path}")

    if os.path.exists(output_file):
        print(f"⏭️ PDF already exists: {output_file}, skipping.\n")
        logging.debug(f"PDF already exists, skipping: {output_file}")
        return

    images = sorted(
        [
            os.path.join(chapter_path, f)
            for f in os.listdir(chapter_path)
            if f.lower().endswith((".webp", ".jpg", ".jpeg", ".png"))
        ]
    )
    logging.debug(f"Found {len(images)} image(s) in chapter: {chapter_path}")

    if not images:
        print(f"⚠️ No images found in {chapter_path}, skipping.\n")
        new_chapter_path = f"{chapter_path}-xxx"
        os.rename(chapter_path, new_chapter_path)
        print(f"📛 Renamed incomplete chapter to: {new_chapter_path}\n")
        logging.debug(f"No images found, renamed to: {new_chapter_path}")
        return

    converted_images = []
    failed_files = []
    for img_path in images:
        try:
            with Image.open(img_path) as img:
                rgb_img = img.convert("RGB")
                jpg_path = img_path + ".jpg"
                rgb_img.save(jpg_path, "JPEG")
                converted_images.append(jpg_path)
        except Exception as e:
            failed_files.append(img_path.split("/")[-1])
            logging.debug(f"Image conversion failed for {img_path}: {e}")

    if failed_files:
        print(f"⚠️ Failed to convert images: {failed_files}")
        logging.debug(f"Failed files: {failed_files}")

    if not converted_images:
        print(
            f"❌ All images in {chapter_path} failed to convert, skipping PDF generation."
        )
        new_chapter_path = f"{chapter_path}-xxx"
        os.rename(chapter_path, new_chapter_path)
        print(f"📛 Renamed incomplete chapter to: {new_chapter_path}\n")
        logging.debug(f"All images failed, renamed to: {new_chapter_path}")
        return

    try:
        with open(output_file, "wb") as f:
            f.write(img2pdf.convert(converted_images))
        print(f"✅ PDF created: {output_file}")
        logging.debug(f"PDF successfully created: {output_file}")
    except Exception as e:
        print(f"❌ Failed to create PDF for {chapter_path}: {e}")
        new_chapter_path = f"{chapter_path}-xxx"
        os.rename(chapter_path, new_chapter_path)
        print(f"📛 Renamed incomplete chapter to: {new_chapter_path}\n")
        logging.debug(
            f"PDF creation failed, renamed to: {new_chapter_path}, error: {e}"
        )
        return

    print(f"🗑️ Removed folder: {chapter_path}\n")
    logging.debug(f"Cleaning up temporary JPEGs and removing folder: {chapter_path}")
    for temp_img in converted_images:
        os.remove(temp_img)
    shutil.rmtree(chapter_path)
