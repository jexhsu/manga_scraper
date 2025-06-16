from .base_spider import BaseMangaSpider

class DemonSlayerSpider(BaseMangaSpider):
    """
    Spider class to scrape manga chapters and images from 'Demon Slayer' website.
    Inherits from BaseMangaSpider for common functionality.
    """
    # Unique spider name used for CLI execution
    name = "demon_slayer"
    
    # Internal identifier for the site
    site_name = "demon_slayer"
    
    # Domains allowed for crawling and image hosting
    allowed_domains = ['www.demonslayerr.com']
    
    # CSS selector to extract chapter URLs from the main listing page
    chapter_list_selector = 'div.d-flex a::attr(href)'
    
    # Regex pattern to extract chapter index from the URL
    chapter_pattern = r'/(\d+)$'
    
    # Boolean to enable pagination logic
    paginate = True

    # URL to start crawling chapter list
    start_url = "https://www.demonslayerr.com/demon-slayer/manga/chapters"
    
    # Template to build chapter URLs dynamically
    url_template = "https://www.demonslayerr.com/demon-slayer/manga/chapters/{chapter}/"
    
    # CSS selector to extract image elements from chapter pages
    image_selector = "div img.w-100"
