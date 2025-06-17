# manga_scraper/utils/chapter_list_parser.py
import re
from manga_scraper.utils.paginator import ChapterPaginator
from manga_scraper.utils.chapter_url_processor import process_chapter_urls
from manga_scraper.utils.chapter_display import print_chapter_summary
from manga_scraper.utils.chapter_checker import check_chapter_completion_and_get_start_index

def parse_chapter_list(response, spider):
    """
    Parse chapter list from the response, handling pagination if enabled.
    
    Args:
        response (scrapy.http.Response): The response object from Scrapy.
        spider (scrapy.Spider): The spider instance.
    
    Returns:
        tuple: A tuple containing:
            - chapter_map (dict): Mapping of chapter keys to URLs.
            - chapter_list (list): List of chapter identifiers.
            - chapter_index (int): Starting index for downloading chapters.
            - next_page_url (str): URL of the next page if pagination is enabled, otherwise None.
    """
    if spider.paginate:
        spider.paginator.extract_chapters(response)
        if spider.paginator.has_more_pages:
            next_page = spider.paginator.next_page_url()
            return None, None, None, next_page
        
        raw_chapters = spider.paginator.all_chapters
    else:
        raw_chapters = response.css(spider.chapter_list_selector).re(spider.chapter_pattern)

    # Process raw chapter data into structured format
    chapter_map, chapter_list = process_chapter_urls(raw_chapters, spider.anti_scraping_url)
    print_chapter_summary(chapter_list)

    # Determine where to start downloading based on completed chapters
    chapter_index = check_chapter_completion_and_get_start_index(
        spider.root_dir,
        spider.site_name,
        chapter_list,
        spider
    )

    return chapter_map, chapter_list, chapter_index, None