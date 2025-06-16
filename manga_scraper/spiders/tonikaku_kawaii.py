from .base_spider import BaseMangaSpider

class TonikakuKawaiiSpider(BaseMangaSpider):
    """
    Spider class to scrape manga chapters and images from 'Tonikaku Kawaii' website.
    Inherits from BaseMangaSpider for common functionality.
    """
    # Unique spider name used for CLI execution
    name = "tonikaku_kawaii"
    
    # Internal identifier for the site
    site_name = "tonikaku_kawaii"
    
    # Domains allowed for crawling and image hosting
    allowed_domains = ['w3.tonikakukawaii.com']
    
    # CSS selector to extract chapter URLs from the main listing page
    chapter_list_selector = 'li a::attr(href)'
    
    # Regex pattern to extract chapter index from the URL
    chapter_pattern = r'chapter-(.+?)/'

    # URL to start crawling chapter list
    start_url = "https://w3.tonikakukawaii.com"

    # Template to build chapter URLs dynamically
    url_template = "https://w3.tonikakukawaii.com/manga/tonikaku-cawaii-chapter-{chapter}/"
    
    # CSS selector to extract image elements from chapter pages
    image_selector = "div img.aligncenter"
