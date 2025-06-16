from .base_spider import BaseMangaSpider

class TooManyLosingHeroinesSpider(BaseMangaSpider):
    """
    Spider class to scrape manga chapters and images from 'Too Many Losing Heroines' website.
    Inherits from BaseMangaSpider for common functionality.
    """
    # Unique spider name used for CLI execution
    name = "too_many_losing_heroines"
    
    # Internal identifier for the site
    site_name = "too_many_losing_heroines"
    
    # Allowed domains for crawling and image hosting
    allowed_domains = ['toomanylosingheroines.com']
    
    # CSS selector to extract chapter URLs from the main chapter listing page
    chapter_list_selector = 'div li a::attr(href)'
    
    # Regex pattern to extract chapter number from the URL
    chapter_pattern = r'chapter-(.+?)/'
    
    # URL to start scraping from
    start_url = "https://toomanylosingheroines.com"

    # Template for constructing chapter URLs
    url_template = "https://toomanylosingheroines.com/manga/too-many-losing-heroines-chapter-{chapter}/"
    
    # CSS selector to extract image URLs from chapter page
    image_selector = "div img.aligncenter"
