from .base_spider import BaseMangaSpider

class DarkGatheringSpider(BaseMangaSpider):
    """
    Spider class to scrape manga chapters and images from 'Dark Gathering' website.
    Inherits from BaseMangaSpider for common functionality.
    """
    # Unique spider name used for CLI execution
    name = "dark_gathering"
    
    # Internal identifier for the site
    site_name = "dark_gathering"
    
    # Domains allowed for crawling and image hosting
    allowed_domains = ['dark-gathering.com']
    
    # CSS selector to extract chapter URLs from the main listing page
    chapter_list_selector = '#ceo_latest_comics_widget-3 ul li a::attr(href)'
    
    # Regex pattern to extract chapter index from the URL
    chapter_pattern = r'chapter-(.+?)/'

    # URL to start crawling chapter list
    start_url = "https://dark-gathering.com"
    
    # Template to build chapter URLs dynamically
    url_template = "https://dark-gathering.com/manga/dark-gathering-chapter-{chapter}/"
    
    # CSS selector to extract image elements from chapter pages
    image_selector = "img"
