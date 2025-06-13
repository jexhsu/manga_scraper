from .base_spider import BaseMangaSpider

class GrandBlueSpider(BaseMangaSpider):
    """
    Spider class to scrape manga chapters and images from 'Grand Blue' website.
    Inherits from BaseMangaSpider for common functionality.
    """
    # Unique spider name used for CLI execution
    name = "grand_blue"
    
    # Internal identifier for the site
    site_name = "grand_blue"
    
    # Allowed domains for crawling and image hosting
    allowed_domains = ['w38.readgrandblue.com', 'eu2.contabostorage.com']
    
    # Initial chapter list (can be empty; will be populated using chapter_list_selector)
    chapter_list = [""]
    
    # CSS selector to extract chapter URLs from the main listing page
    chapter_list_selector = 'div a::attr(href)'
    
    # Regex pattern to extract chapter index from the URL
    chapter_pattern = r'chapter-(.+?)/'
    
    # Starting URL to begin scraping
    start_url = "https://w38.readgrandblue.com"
    
    # Starting chapter index for scraping (used to skip early chapters)
    start_chapter = 45

    # Template to dynamically construct chapter URLs
    url_template = "https://w38.readgrandblue.com/manga/grand-blue-chapter-{chapter}/"
    
    # CSS selector to extract image elements from the chapter page
    image_selector = "img"
    
    # List of allowed image-host domains for filtering
    image_host_filters = allowed_domains

    # File extension for the image files (e.g., '.jpg', '.png')
    file_ext = ".jpg"
