from .base_spider import BaseMangaSpider

class TokyoGhoulSpider(BaseMangaSpider):
    """
    Spider class to scrape manga chapters and images from 'Demo Manga' website.
    Inherits from BaseMangaSpider for common functionality.
    """
    name = "tokyo_ghoul"
    site_name = "tokyo_ghoul"
    allowed_domains = ['tgmanga.com']

    # List of chapter URLs to start scraping from
    chapter_list = [""]
    
    # CSS selector to extract chapter URLs from the page
    chapter_list_selector = 'li a::attr(href)'
    
    # Regular expression pattern to extract chapter number from the URL
    chapter_pattern = r'chapter-(.+?)/'
    
    # Boolean value to determine if pagination is enabled
    paginate = False
    
    # URL to start scraping from
    start_url = "https://tgmanga.com"
    
    # Starting chapter index for scraping
    start_chapter = 60

    # Template for constructing chapter URLs
    url_template = "https://tgmanga.com/manga/tokyo-ghoul-chapter-{chapter}/"
    
    # CSS selector to extract image URLs from chapter page
    image_selector = "img.lazyloaded, img.alignnone, img.aligncenter"
    
    # List of allowed domain names for the image host
    image_host_filters = allowed_domains
    
    # File extension for the image files (e.g., '.jpg', '.png')
    file_ext = ".jpeg"