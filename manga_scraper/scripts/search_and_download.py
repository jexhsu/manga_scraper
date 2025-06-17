from scrapy.crawler import CrawlerProcess
import os
from scrapy.utils.project import get_project_settings
from playwright.sync_api import sync_playwright
import time
import logging
import re

import json


class MangaSearchDownloader:
    """🎯 Interactive manga search & download tool using Playwright + Scrapy."""

    CACHE_FILE = (
        "manga_park_search_cache.json"  # Cache file to store previous search results
    )

    def __init__(self):
        """Initialize with Scrapy project settings and dynamic log level."""
        self.settings = get_project_settings()
        log_level = os.getenv("LOG_LEVEL", "INFO")
        self.settings.set("LOG_LEVEL", log_level.upper())
        # Load cache at init, or create empty cache dict if file not exists
        self.cache = self.load_cache()

    def load_cache(self):
        """Load cached manga search results from JSON file."""
        if os.path.exists(self.CACHE_FILE):
            try:
                with open(self.CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logging.warning(f"⚠️ Failed to load cache file: {e}")
                return {}
        else:
            return {}

    def save_cache(self):
        """Save current cache dict to JSON file."""
        try:
            with open(self.CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"❌ Failed to save cache file: {e}")

    def search_manga(self, query, max_retries=3, retry_delay=3):
        """
        🔍 Search manga on MangaPark by constructing search URL directly,
        without filling form or clicking UI elements.
        """

        # First check if query already cached
        if query in self.cache:
            logging.info(f"🗂️ Using cached search results for '{query}'.")
            return self.cache[query]

        from urllib.parse import quote_plus

        base_url = "https://mangapark.io/search?word="
        encoded_query = quote_plus(query)
        search_url = f"{base_url}{encoded_query}&sortby=field_score"

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
                    results = page.locator("h3.font-bold a.link-hover").all()
                    manga_list = []

                    print("\n🎉 Search Results:")
                    for i, link in enumerate(results[:20], 1):
                        href = link.get_attribute("href")
                        title = link.inner_text().strip()
                        manga_id = href.split("/")[-1]
                        manga_list.append(
                            {
                                "index": i,
                                "title": title,
                                "url": f"https://mangapark.io{href}",
                                "manga_id": manga_id,
                            }
                        )
                        print(f"  {i:02d}. 📚 {title}")

                    browser.close()

                    # Cache the search results for this query
                    self.cache[query] = manga_list
                    self.save_cache()

                    return manga_list

            except Exception as e:
                logging.error(f"❌ Error during search (attempt {attempt}): {e}")
                time.sleep(retry_delay)

        logging.error("🚫 All search attempts failed.")
        return []

    def run_spider(self, manga_id, manga_name):
        """🕷️ Run Scrapy spider for selected manga and save the selection."""
        # Save manga_id and name to cache under special key for downloaded mangas
        downloaded = self.cache.get("_downloaded_mangas", {})
        downloaded[manga_name] = manga_id
        self.cache["_downloaded_mangas"] = downloaded
        self.save_cache()

        spider_class = type(
            f"MangaPark_{manga_name}Spider",
            (BaseMangaParkSpider,),
            {
                "name": f"{manga_name.lower().replace(' ', '_')}",
                "manga_id": manga_id,
            },
        )

        logging.info(f"📥 Starting download for: {manga_name}")
        process = CrawlerProcess(self.settings)
        process.crawl(spider_class)
        process.start()


def parse_input(input_str):
    """
    🧠 Parse multi-choice input like '1,2,4-6' to [1, 2, 4, 5, 6]
    """
    parts = re.split(r"\s*,\s*", input_str)
    numbers = []
    for part in parts:
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

    # 🌈 Prompt user to choose log level
    while True:
        log_level = (
            input(
                "🛠️ Choose log level (DEBUG / INFO / WARNING / ERROR), default [ERROR]: "
            )
            or "ERROR"
        )
        log_level = log_level.upper()
        if log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            break
        else:
            print("⚠️ Invalid log level. Please enter DEBUG, INFO, WARNING, or ERROR.")

    os.environ["LOG_LEVEL"] = log_level
    logging.basicConfig(level=getattr(logging, log_level, logging.INFO))

    downloader = MangaSearchDownloader()

    # Step 1: Show cached downloaded mangas, if any
    downloaded = downloader.cache.get("_downloaded_mangas", {})
    if downloaded:
        print("\n🗂️ Cached downloaded mangas found:")
        for i, (name, mid) in enumerate(downloaded.items(), 1):
            print(f"  {i:02d}. 📥 {name} (ID: {mid})")

        use_cache = (
            input("\n❓ Download from cached manga(s)? (Y/n): ").strip().lower() or "y"
        )

        if use_cache == "y":
            while True:
                choice = input(
                    "\n🎯 Enter cached manga number(s) to download again (e.g. 1,2 or 3), or 'q' to skip: "
                ).strip()
                if choice.lower() == "q":
                    break
                indices = parse_input(choice)
                invalid = [i for i in indices if i < 1 or i > len(downloaded)]
                if invalid:
                    logging.warning(f"❗ Invalid selections: {invalid}")
                    continue
                items = list(downloaded.items())
                for i in indices:
                    manga_name, manga_id = items[i - 1]
                    logging.info(f"✅ Queued cached: {manga_name}")
                    downloader.run_spider(manga_id, manga_name)
                break  # finish cache download step

    # Step 2: Ask user if want to search new manga to download
    want_search = (
        input("\n❓ Search new manga to download? (y/N): ").strip().lower() or "n"
    )
    if want_search == "y":
        while True:
            query = input("\n🔎 Enter manga title to search (or 'q' to quit): ").strip()
            if query.lower() == "q":
                print("👋 Bye!")
                return
            if not query:
                print("⚠️ Search query cannot be empty.")
                continue

            results = downloader.search_manga(query)
            if not results:
                logging.warning("⚠️ No matching manga found.")
                continue

            print("\n🎉 Search Results:")
            for i, manga in enumerate(results, 1):
                print(f"  {i:02d}. 📚 {manga['title']}")

            while True:
                choice = input(
                    "\n🎯 Enter manga number(s) to download (e.g. 1,2 or 3-5), or 'q' to quit search: "
                ).strip()
                if choice.lower() == "q":
                    break
                indices = parse_input(choice)
                invalid = [i for i in indices if i < 1 or i > len(results)]
                if invalid:
                    logging.warning(f"❗ Invalid selections: {invalid}")
                    continue
                for i in indices:
                    selected = results[i - 1]
                    logging.info(f"✅ Queued: {selected['title']}")
                    downloader.run_spider(selected["manga_id"], selected["title"])
                break  # after downloading selected

            # Ask if want to search again or quit
            again = input("\n❓ Search another manga? (y/N): ").strip().lower() or "n"
            if again != "y":
                break

    print("👋 Bye!")


if __name__ == "__main__":
    from manga_scraper.spiders.manga_park import BaseMangaParkSpider

    main()
