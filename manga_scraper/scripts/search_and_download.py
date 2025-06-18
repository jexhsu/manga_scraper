import os
import subprocess
import logging
import re
import json
from pathlib import Path
import time
from playwright.sync_api import sync_playwright


class MangaSearchDownloader:
    """🎯 Interactive manga search & download tool using Playwright + Scrapy."""

    CACHE_FILE = "manga_park_search_cache.json"  # Cache file for search results
    SPIDERS_FILE = "manga_scraper/spiders/manga_park.py"  # Main spiders file

    def __init__(self):
        """Initialize with basic logging configuration."""
        log_level = os.getenv("LOG_LEVEL", "ERROR").upper()
        logging.basicConfig(
            level=getattr(logging, log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            force=True,
        )
        self.cache = self.load_cache()
        self._ensure_spiders_file()
        self.existing_spiders = self._load_existing_spiders()

    def _ensure_spiders_file(self):
        """Ensure spiders file exists with base class."""
        Path(self.SPIDERS_FILE).parent.mkdir(parents=True, exist_ok=True)
        if not Path(self.SPIDERS_FILE).exists():
            with open(self.SPIDERS_FILE, "w", encoding="utf-8") as f:
                f.write(
                    """from .base_spider import BaseMangaSpider

class BaseMangaParkSpider(BaseMangaSpider):
    \"\"\"Base spider for MangaPark websites.\"\"\"
    name = None
    abstract = True
    allowed_domains = ["mangapark.io"]
    chapter_list_selector = "div.space-x-1 a::attr(href)"
    anti_scraping_url = True
    root_dir = "downloads/manga_park"
    use_playwright = True
    image_selector = "div[data-name='image-show'] img"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chapter_pattern = rf"{self.manga_id}/(.+)"
        self.start_url = f"https://mangapark.io/title/{self.manga_id}"
        self.url_template = f"https://mangapark.io/title/{self.manga_id}/{{chapter}}/"
"""
                )

    def _load_existing_spiders(self):
        """Load existing spider names from spiders file."""
        if not os.path.exists(self.SPIDERS_FILE):
            return set()

        with open(self.SPIDERS_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        return set(re.findall(r"name\s*=\s*\"([^\"]+)", content))

    def _add_spider_to_file(self, spider_name, manga_id):
        """Add a new spider class to the spiders file if it doesn't exist."""
        if spider_name in self.existing_spiders:
            logging.info(f"🔄 Spider '{spider_name}' already exists, skipping creation")
            return False

        class_name = "".join(word.capitalize() for word in spider_name.split("_"))
        with open(self.SPIDERS_FILE, "a", encoding="utf-8") as f:
            f.write(
                f"""
class {class_name}Spider(BaseMangaParkSpider):
    \"\"\"Spider for {spider_name.replace('_', ' ')} manga.\"\"\"
    name = "{spider_name}"
    manga_id = "{manga_id}"
"""
            )
        self.existing_spiders.add(spider_name)
        return True

    def load_cache(self):
        """Load cached manga search results from JSON file."""
        if os.path.exists(self.CACHE_FILE):
            try:
                with open(self.CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logging.warning(f"⚠️ Failed to load cache file: {e}")
                return {}
        return {}

    def save_cache(self):
        """Save current cache dict to JSON file."""
        try:
            with open(self.CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"❌ Failed to save cache file: {e}")

    def search_manga(self, query, max_retries=3, retry_delay=3):
        """🔍 Search manga on MangaPark and return results."""
        if query in self.cache:
            logging.info(f"🗂️ Using cached search results for '{query}'.")
            return self.cache[query]

        from urllib.parse import quote_plus

        base_url = "https://mangapark.io/search?word="
        search_url = f"{base_url}{quote_plus(query)}&sortby=field_score"

        for attempt in range(1, max_retries + 1):
            logging.info(
                f"🔁 Attempt {attempt} of {max_retries} to search for '{query}'..."
            )
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    page.goto(search_url, timeout=60000, wait_until="networkidle")
                    page.wait_for_selector("h3.font-bold a.link-hover", timeout=15000)

                    results = []
                    for i, link in enumerate(
                        page.locator("h3.font-bold a.link-hover").all()[:20], 1
                    ):
                        href = link.get_attribute("href")
                        title = link.inner_text().strip()
                        manga_id = href.split("/")[-1]
                        results.append(
                            {
                                "index": i,
                                "title": title,
                                "url": f"https://mangapark.io{href}",
                                "manga_id": manga_id,
                            }
                        )

                    browser.close()
                    self.cache[query] = results
                    self.save_cache()
                    return results

            except Exception as e:
                logging.error(f"❌ Error during search (attempt {attempt}): {e}")
                time.sleep(retry_delay)

        logging.error("🚫 All search attempts failed.")
        return []

    def run_spider(self, manga_id, manga_name):
        """🕷️ Execute Scrapy spider via command line."""
        # Save to cache
        downloaded = self.cache.get("_downloaded_mangas", {})
        downloaded[manga_name] = manga_id
        self.cache["_downloaded_mangas"] = downloaded
        self.save_cache()

        # Generate spider name
        spider_name = manga_name.lower().replace(" ", "_")
        logging.info(f"📥 Starting download for: {manga_name}")

        # Only add spider if it doesn't exist
        spider_created = self._add_spider_to_file(spider_name, manga_id)
        if spider_created:
            logging.debug(f"➕ Created new spider: {spider_name}")

        try:
            # Build and execute scrapy command
            cmd = [
                "scrapy",
                "crawl",
                spider_name,
                "-s",
                f"LOG_LEVEL={os.getenv('LOG_LEVEL', 'ERROR')}",
            ]
            subprocess.run(cmd, check=True, cwd=os.getcwd())
        except subprocess.CalledProcessError as e:
            logging.error(f"❌ Spider execution failed: {e}")
        except Exception as e:
            logging.error(f"❌ Unexpected error: {e}")


def parse_input(input_str):
    """🧠 Parse multi-choice input like '1,2,4-6' to [1, 2, 4, 5, 6]"""
    numbers = []
    for part in re.split(r"\s*,\s*", input_str):
        if "-" in part:
            start, end = map(int, part.split("-"))
            numbers.extend(range(start, end + 1))
        else:
            try:
                numbers.append(int(part))
            except ValueError:
                pass
    return sorted(set(numbers))


def main():
    """🧭 Main interactive UI for manga search and download."""
    print("🌟 === Manga Search & Downloader === 🌟")

    # Get log level from user
    while True:
        log_level = (
            input(
                "🛠️ Choose log level (DEBUG/INFO/WARNING/ERROR), default [ERROR]: "
            ).upper()
            or "ERROR"
        )
        if log_level in {"DEBUG", "INFO", "WARNING", "ERROR"}:
            break
        print("⚠️ Invalid log level. Please enter DEBUG, INFO, WARNING, or ERROR.")

    os.environ["LOG_LEVEL"] = log_level
    downloader = MangaSearchDownloader()

    # Show cached downloads
    downloaded = downloader.cache.get("_downloaded_mangas", {})
    if downloaded:
        print("\n🗂️ Cached downloaded mangas found:")
        for i, (name, mid) in enumerate(downloaded.items(), 1):
            print(f"  {i:02d}. 📥 {name} (ID: {mid})")

        if input("\n❓ Download from cached manga(s)? (Y/n): ").strip().lower() != "n":
            while True:
                choice = input(
                    "\n🎯 Enter manga number(s) to download (e.g. 1,2 or 3), or 'q' to skip: "
                ).strip()
                if choice.lower() == "q":
                    break

                for i in parse_input(choice):
                    if 1 <= i <= len(downloaded):
                        name, mid = list(downloaded.items())[i - 1]
                        downloader.run_spider(mid, name)

    # New search
    if input("\n❓ Search new manga to download? (y/N): ").strip().lower() == "y":
        while True:
            query = input("\n🔎 Enter manga title to search (or 'q' to quit): ").strip()
            if query.lower() == "q":
                break

            results = downloader.search_manga(query)
            if results:
                print("\n🎉 Search Results:")
                for i, manga in enumerate(results, 1):
                    print(f"  {i:02d}. 📚 {manga['title']}")

                choice = input(
                    "\n🎯 Enter manga number(s) to download (e.g. 1,2 or 3-5), or 'q' to quit: "
                ).strip()
                if choice.lower() != "q":
                    for i in parse_input(choice):
                        if 1 <= i <= len(results):
                            selected = results[i - 1]
                            downloader.run_spider(
                                selected["manga_id"], selected["title"]
                            )

            if input("\n❓ Search another manga? (y/N): ").strip().lower() != "y":
                break

    print("\n👋 Bye!")


if __name__ == "__main__":
    main()
