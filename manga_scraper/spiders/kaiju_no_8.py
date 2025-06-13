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
    allowed_domains = ['kaiju-no8.com', 'cdn.black-clover.org']
    
    # Initial chapter list (can be empty; will be populated from selector)
    chapter_list = [""]
    
    # CSS selector to extract chapter URLs from the main listing page
    chapter_list_selector = 'ul li a::attr(href)'
    
    # Regex pattern to extract chapter index from the URL
    chapter_pattern = r'chapter-(.+?)/'
    
    # Boolean to enable pagination logic (False if chapter_list_selector is used)
    paginate = False

    # URL to start crawling chapter list
    start_url = "https://kaiju-no8.com"
    
    # Starting index to control which chapter to begin scraping from
    start_chapter = 0

    # Template to build chapter URLs dynamically
    url_template = "https://kaiju-no8.com/manga/kaiju-no-8-chapter-{chapter}/"
    
    # CSS selector to extract image elements from chapter pages
    image_selector = "img"
    
    # List of image-host domains for filtering
    image_host_filters = allowed_domains

    # File extension for saved images (default .webp)
    file_ext = ".webp"
