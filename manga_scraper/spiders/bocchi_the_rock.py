from .base_spider import BaseMangaSpider

class BocchitheRockSpider(BaseMangaSpider):
    """
    Spider class to scrape manga chapters and images from 'Bocchi the Rock' website.
    Inherits from BaseMangaSpider for common functionality.
    """
    # Unique spider name used for CLI execution
    name = "bocchi_the_rock"
    
    # Internal identifier for the site
    site_name = "bocchi_the_rock"
    
    # Domains allowed for crawling and image hosting
    allowed_domains = ['w3.bocchitherockmanga.com']
    
    # CSS selector to extract chapter URLs from the main listing page
    chapter_list_selector = 'ul li a::attr(href)'
    
    # Regex pattern to extract chapter index from the URL
    chapter_pattern = r'chapter-(.+?)/'

    # URL to start crawling chapter list
    start_url = "https://w3.bocchitherockmanga.com"

    # Template to build chapter URLs dynamically
    url_template = "https://w3.bocchitherockmanga.com/manga1/bocchi-the-rock-chapter-{chapter}/"
    
    # CSS selector to extract image elements from chapter pages
    image_selector = "div img.aligncenter"