from .base_spider import BaseMangaSpider

class TokyoGhoulSpider(BaseMangaSpider):
    """
    Spider class to scrape manga chapters and images from 'Demo Manga' website.
    Inherits from BaseMangaSpider for common functionality.
    """
    # Unique spider name used for CLI execution
    name = "tokyo_ghoul"

    # Internal identifier for the site
    site_name = "tokyo_ghoul"

    # Domains allowed for crawling and image hosting
    allowed_domains = ['tgmanga.com']
    
    # CSS selector to extract chapter URLs from the page
    chapter_list_selector = 'li a::attr(href)'
    
    # Regular expression pattern to extract chapter number from the URL
    chapter_pattern = r'chapter-(.+?)/'
    
    # URL to start scraping from
    start_url = "https://tgmanga.com"

    # Template for constructing chapter URLs
    url_template = "https://tgmanga.com/manga/tokyo-ghoul-chapter-{chapter}/"
    
    # CSS selector to extract image URLs from chapter page
    image_selector = "img.lazyloaded, img.alignnone, img.aligncenter"
