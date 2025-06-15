from .base_spider import BaseMangaSpider

class MangaParkTestSpider(BaseMangaSpider):
    """
    Spider class to scrape manga chapters and images from 'Demo Manga' website.
    Inherits from BaseMangaSpider for common functionality.
    """
    name = "manga_park_test"
    site_name = "manga_park_test"
    allowed_domains = ['mangapark.io', 'demo-manga.com']

    # List of chapter URLs to start scraping from
    chapter_list = [""]
    
    # CSS selector to extract chapter URLs from the page
    chapter_list_selector = 'div.space-x-1 a::attr(href)'
    
    # Regular expression pattern to extract chapter number from the URL
    chapter_pattern = r'76065-en-bocchi-the-rock/(.+)'
    
    # Boolean value to determine if pagination is enabled
    paginate = False
    
    # URL to start scraping from
    start_url = "https://mangapark.io/title/76065-en-bocchi-the-rock"

    anti_scraping_url = True
    
    # Starting chapter index for scraping
    start_chapter = 1

    # Template for constructing chapter URLs
    url_template = "https://mangapark.io/title/76065-en-bocchi-the-rock/{chapter}/"
    
    # CSS selector to extract image URLs from chapter page
    image_selector = "div[data-name='image-show'] img"

    # Enable Playwright
    use_playwright = True  

    # List of allowed domain names for the image host
    image_host_filters = allowed_domains
    
    # File extension for the image files (e.g., '.jpg', '.png')
    file_ext = ".jpeg"