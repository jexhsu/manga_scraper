from .base_spider import BaseMangaSpider

class FrierenAtTheFuneralSpider(BaseMangaSpider):
    """
    Spider class to scrape manga chapters and images from 'Frieren at the Funeral' website.
    Inherits from BaseMangaSpider for common functionality.
    """
    # Unique spider name used for CLI execution
    name = "frieren_at_the_funeral"
    
    # Internal identifier for the site
    site_name = "frieren_at_the_funeral"
    
    # Domains allowed for crawling and image hosting
    allowed_domains = ['sousou-no-frieren.online']
    
    # CSS selector to extract chapter URLs from the main listing page
    chapter_list_selector = 'ul li a::attr(href)'
    
    # Regex pattern to extract chapter index from the URL
    chapter_pattern = r'chapter-(.+?)/'
    
    # URL to start crawling chapter list
    start_url = "https://sousou-no-frieren.online"
    
    # Template to build chapter URLs dynamically
    url_template = "https://sousou-no-frieren.online/manga/sousou-no-frieren-chapter-{chapter}/"
    
    # CSS selector to extract image elements from chapter pages
    image_selector = "img[id^='image-']"
