from .base_spider import BaseMangaSpider

class SpyXFamilySpider(BaseMangaSpider):
    """
    Spider class to scrape manga chapters and images from 'Spy X Family' website.
    Inherits from BaseMangaSpider for common functionality.
    """
    # Unique spider name used for CLI execution
    name = "spy_x_family"
    
    # Internal identifier for the site
    site_name = "spy_x_family"
    
    # Domains allowed for crawling and image hosting
    allowed_domains = ['w2.spyxfamilyseason.com']
    
    # CSS selector to extract chapter URLs from the main listing page
    chapter_list_selector = '#ceo_latest_comics_widget-3 ul li a::attr(href)'
    
    # Regex pattern to extract chapter index from the URL
    chapter_pattern = r'chapter-(.+?)/'

    # URL to start crawling chapter list
    start_url = "https://w2.spyxfamilyseason.com"

    # Template to build chapter URLs dynamically
    url_template = "https://w2.spyxfamilyseason.com/manga/spy-x-family-chapter-{chapter}/"
    
    # CSS selector to extract image elements from chapter pages
    image_selector = "img"
