from .base_spider import BaseMangaSpider

class DandadanSpider(BaseMangaSpider):
    """
    Spider class to scrape manga chapters and images from 'Dandadan Manga' website.
    Inherits from BaseMangaSpider for common functionality.
    """
    # Unique spider name used for CLI execution
    name = "dandadan"
    
    # Internal identifier for the site
    site_name = "dandadan"
    
    # Domains allowed for crawling and image hosting
    allowed_domains = [
        'dandadan.net',
        'cdn.readkakegurui.com',
        'pic.readkakegurui.com',
        'cdn.black-clover.org'
    ]
    
    # Initial chapter list (can be empty; will be populated from selector)
    chapter_list = [""]
    
    # CSS selector to extract chapter URLs from the main listing page
    chapter_list_selector = 'ul li a::attr(href)'
    
    # Regex pattern to extract chapter index from the URL
    chapter_pattern = r'chapter-(.+?)/'
    
    # Boolean to enable pagination logic (False if chapter_list_selector is used)
    paginate = False

    # URL to start crawling chapter list
    start_url = "https://dandadan.net"
    
    # Starting index to control which chapter to begin scraping from
    start_chapter = 0

    # Template to build chapter URLs dynamically
    url_template = "https://dandadan.net/manga/dandadan-chapter-{chapter}/"
    
    # CSS selector to extract image elements from chapter pages
    image_selector = "img"
    
    # List of image-host domains for filtering
    image_host_filters = allowed_domains

    # File extension for saved images
    file_ext = ".webp"
