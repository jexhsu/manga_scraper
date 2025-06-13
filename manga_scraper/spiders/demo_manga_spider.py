from .base_spider import BaseMangaSpider

class DemoMangaSpider(BaseMangaSpider):
    """
    Spider class to scrape manga chapters and images from 'Demo Manga' website.
    Inherits from BaseMangaSpider for common functionality.
    """
    name = "demo_manga_name"
    site_name = "demo_manga_name"
    allowed_domains = ['www.demomanga.com', 'demo-manga.com']

    # List of chapter URLs to start scraping from
    chapter_list = [""]
    
    # CSS selector to extract chapter URLs from the page
    chapter_list_selector = 'div.chapter-list a::attr(href)'
    
    # Regular expression pattern to extract chapter number from the URL
    chapter_pattern = r'chapter-(.+?)/'
    
    # Boolean value to determine if pagination is enabled
    paginate = False
    
    # URL to start scraping from
    start_url = "https://www.demomanga.com/"
    
    # Starting chapter index for scraping
    start_chapter = 0

    # Template for constructing chapter URLs
    url_template = "https://www.demomanga.com/manga/chapters/{chapter}/"
    
    # CSS selector to extract image URLs from chapter page
    image_selector = "div.manga-page img"

    # List of allowed domain names for the image host
    image_host_filters = allowed_domains
    
    # File extension for the image files (e.g., '.jpg', '.png')
    file_ext = ".jpg"