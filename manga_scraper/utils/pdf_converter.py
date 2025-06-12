# pdf_converter.py

import os
from PIL import Image
import img2pdf
import shutil

def convert_chapter_to_pdf(chapter_path):
    chapter_name = os.path.basename(chapter_path)
    output_dir = os.path.dirname(chapter_path)
    output_file = os.path.join(output_dir, f"{chapter_name}.pdf")

    if os.path.exists(output_file):
        print(f"⏭️ PDF already exists: {output_file}, skipping.\n")
        return

    images = sorted([
        os.path.join(chapter_path, f)
        for f in os.listdir(chapter_path)
        if f.lower().endswith(('.webp', '.jpg', '.jpeg', '.png'))
    ])

    if not images:
        print(f"⚠️ No images found in {chapter_path}, skipping.\n")
        return

    converted_images = []
    for img_path in images:
        try:
            with Image.open(img_path) as img:
                rgb_img = img.convert("RGB")
                jpg_path = img_path + ".jpg"
                rgb_img.save(jpg_path, "JPEG")
                converted_images.append(jpg_path)
        except Exception as e:
            print(f"⚠️ Failed to convert image {img_path}: {e}, skipping.")

    if not converted_images:
        print(f"❌ All images in {chapter_path} failed to convert, skipping PDF generation.")
        return

    try:
        with open(output_file, "wb") as f:
            f.write(img2pdf.convert(converted_images))
        print(f"✅ PDF created: {output_file}")
    except Exception as e:
        print(f"❌ Failed to create PDF for {chapter_name}: {e}")
        return

    print(f"🗑️ Removed folder: {chapter_path}\n")
    for temp_img in converted_images:
        os.remove(temp_img)
    shutil.rmtree(chapter_path)
