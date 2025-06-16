from .base_spider import BaseMangaSpider

class KaijuNo8Spider(BaseMangaSpider):
    """
    Spider class to scrape manga chapters and images from the 'Kaiju No. 8' website.
    Inherits from BaseMangaSpider for common functionality.
    """
    # Unique spider name used for CLI execution
    name = "kaiju_no_8"
    
    # Internal identifier for the site
    site_name = "kaiju_no_8"
    
    # Domains allowed for crawling and image hosting
    allowed_domains = ['kaiju-no8.com']
    
    # CSS selector to extract chapter URLs from the main listing page
    chapter_list_selector = 'ul li a::attr(href)'
    
    # Regex pattern to extract chapter index from the URL
    chapter_pattern = r'chapter-(.+?)/'

    # URL to start crawling chapter list
    start_url = "https://kaiju-no8.com"

    # Template to build chapter URLs dynamically
    url_template = "https://kaiju-no8.com/manga/kaiju-no-8-chapter-{chapter}/"
    
    # CSS selector to extract image elements from chapter pages
    image_selector = "img"
