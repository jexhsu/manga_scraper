import scrapy
import os
import img2pdf
from PIL import Image
import shutil
import sys
import logging
import re

# Disable Scrapy's default logs
logging.getLogger('scrapy').setLevel(logging.WARNING)

class BaseMangaSpider(scrapy.Spider):
    name = "base_manga_spider"
    site_name = "site_name"
    allowed_domains = ["example.com"]
    chapter_list = [""]                    
    chapter_list_selector = 'a.chapter-link::attr(href)'  
    chapter_pattern = r'chapter-(\d+)'
    start_chapter = 0
    url_template = "https://example.com/manga/chapter-{chapter}/"
    start_url = "https://example.com"
    image_selector = "img.page-image"
    image_attr = "src"
    file_ext = ".jpg"
    root_dir = "downloads"

    custom_settings = {
        'LOG_LEVEL': 'ERROR',
        'TELNETCONSOLE_ENABLED': False
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_progress_length = 0

    def start_requests(self):
        print(f"\n🚀 Starting download for site: {self.site_name}\n")
        yield scrapy.Request(url=self.start_url, callback=self.parse_chapter_list)


    def parse_chapter_list(self, response):
        """Parse the chapter list page and extract all chapters"""
        raw_chapters = response.css(self.chapter_list_selector).re(self.chapter_pattern)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_chapters = []
        for chap in raw_chapters:
            if chap not in seen:
                seen.add(chap)
                unique_chapters.append(chap)

        # Custom sorting function to handle both simple and special chapter numbers like '38-5'
        def chapter_sort_key(chap):
            # Match chapter number and possible suffix like '38-5'
            match = re.match(r'(\d+)(?:-(\d+))?', chap)
            if match:
                main_num = int(match.group(1))  # The main chapter number
                sub_num = int(match.group(2) or 0)  # The sub-number (default to 0 if no suffix)
                return (main_num, sub_num)
            return (float('inf'), 0)  # Handle any non-matching entries as very high numbers

        # Sort chapters based on the custom sorting key
        self.chapter_list = sorted(unique_chapters, key=chapter_sort_key)

        print(f"📚 Found {len(self.chapter_list)} unique chapters")
        print(f"📚 Unique chapter list: {self.chapter_list}")

        if self.start_chapter >= len(self.chapter_list) or self.start_chapter < 0:
                  print(f"⚠️ start_chapter {self.start_chapter} out of range, reset to 0")
                  self.start_chapter = 0
                  
        # Check if start_chapter exists in chapter_list and set it as the new start index
        try:
            # Find the position of the chapter in the sorted list and use that as the new start_chapter
            self.chapter_index = self.chapter_list.index(str(self.start_chapter))
            print(f"📍 Starting download from chapter {self.start_chapter} at index {self.chapter_index}")
        except ValueError:
            # If start_chapter is not found, reset to the first chapter
            print(f"⚠️ start_chapter {self.start_chapter} not found, resetting to index 0")
            self.chapter_index = 0
        
        if self.chapter_list:
            yield scrapy.Request(
                url=self.url_template.format(chapter=self.chapter_list[self.chapter_index]),
                callback=self.parse_chapter,
                meta={'chapter': self.chapter_list[self.chapter_index]},
                errback=self.handle_error  # Set the error handler here
            )
        else:
            print("⚠️ No chapters found")

    def parse_chapter(self, response):
        chapter = response.meta['chapter']
        img_urls = response.css(f"{self.image_selector}::attr({self.image_attr})").getall()
        total = len(img_urls)

        if total == 0:
            print(f"\n⚠️ Chapter {chapter}: No images found, skipping.\n")
            yield from self.next_chapter()
            return

        folder = os.path.join(self.root_dir, self.site_name, f"chapter-{chapter}")
        os.makedirs(folder, exist_ok=True)

        existing = len([f for f in os.listdir(folder) if f.endswith(self.file_ext)])
        pdf_file = os.path.join(self.root_dir, self.site_name, f"chapter-{chapter}.pdf")
        if os.path.exists(pdf_file):
                print(f"\n✅ Chapter {chapter}: Already downloaded, skip.")
                if os.path.exists(folder):
                    shutil.rmtree(folder)
                    print(f"🗑️ Removed folder: {folder}\n")
                yield from self.next_chapter()
                return

        print(f"\n📥 Chapter {chapter}: Downloading {total} images...")
        self.last_progress_length = 0
        
        yield scrapy.Request(
            url=img_urls[0],
            callback=self.download_image,
            errback=self.handle_error,  # Set the error handler here too
            meta={
                'chapter': chapter,
                'img_urls': img_urls,
                'index': 0,
                'folder': folder,
                'total': total,
                'downloaded': 0
            },
            dont_filter=True
        )

    def download_image(self, response):
        chapter = response.meta['chapter']
        img_urls = response.meta['img_urls']
        index = response.meta['index']
        folder = response.meta['folder']
        total = response.meta['total']
        downloaded = response.meta['downloaded'] + 1

        # Check for a failed image download (non-image or error response)
        if response.status != 200:
            print(f"❌ Error downloading image for chapter {chapter}, skipping entire chapter.")
            yield from self.next_chapter()
            return

        ext = os.path.splitext(img_urls[index])[1].split('?')[0].lower() or self.file_ext
        filename = f"{index+1:03d}{ext}"
        path = os.path.join(folder, filename)

        try:
            with open(path, 'wb') as f:
                f.write(response.body)
        except Exception as e:
            print(f"❌ Error saving image {filename} for chapter {chapter}: {e}")
            yield from self.next_chapter()
            return

        progress_text = f"⏳ Chapter {chapter}: {self.progress_bar(downloaded, total)} ({downloaded}/{total})"
        self.update_progress(progress_text)

        if index + 1 < total:
            yield scrapy.Request(
                url=img_urls[index + 1],
                callback=self.download_image,
                errback=self.handle_error,
                meta={
                    'chapter': chapter,
                    'img_urls': img_urls,
                    'index': index + 1,
                    'folder': folder,
                    'total': total,
                    'downloaded': downloaded
                },
                dont_filter=True
            )
        else:
            self.clear_progress()
            print(f"\n✅ Chapter {chapter}: Download completed!")
            self.convert_chapter_to_pdf(folder)
            yield from self.next_chapter()

    def next_chapter(self):
        self.chapter_index += 1
        if self.chapter_index < len(self.chapter_list):
            next_chapter = self.chapter_list[self.chapter_index]
            yield scrapy.Request(
                url=self.url_template.format(chapter=next_chapter),
                callback=self.parse_chapter,
                meta={'chapter': next_chapter},
                errback=self.handle_error  # Set the error handler here too
            )
        else:
            print("\n🎉 All chapters downloaded and converted!\n")

    def handle_error(self, failure):
        """Error handling when a chapter fails to download"""
        chapter = failure.request.meta['chapter']
        print(f"\n❌ Error occurred while downloading chapter {chapter}: {failure.value}\n")
        yield from self.next_chapter()

    def convert_chapter_to_pdf(self, chapter_path):
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


    def progress_bar(self, current, total, width=20):
        filled = int(current / total * width) if total > 0 else 0
        return "[" + "█" * filled + "-" * (width - filled) + "]"

    def update_progress(self, text):
        sys.stdout.write("\r" + " " * self.last_progress_length)
        sys.stdout.write("\r" + text)
        sys.stdout.flush()
        self.last_progress_length = len(text)

    def clear_progress(self):
        sys.stdout.write("\r" + " " * self.last_progress_length + "\r")
        sys.stdout.flush()
        self.last_progress_length = 0
