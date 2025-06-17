import re
from manga_scraper.utils.chapter_sorter import ChapterSorter


def process_chapter_urls(raw_chapters, anti_scraping_url):
    if anti_scraping_url:
        descending_chapter_map = {}
        pattern = re.compile(r'(?:ch|chapter)-0*(\d+(?:-\d+)*)', re.IGNORECASE)
        for raw in raw_chapters:
            match = pattern.search(raw)
            chapter_key = match.group(1) if match else raw
            descending_chapter_map[chapter_key] = raw

        ascending_chapter_map = {
            k: v for k, v in sorted(descending_chapter_map.items(), 
                                    key=lambda item: int(re.search(r'\d+', item[0]).group()))
        }

        return ascending_chapter_map, list(ascending_chapter_map.keys())
    else:
        sorted_chapters = ChapterSorter.sort_and_deduplicate(raw_chapters)
        return None, sorted_chapters