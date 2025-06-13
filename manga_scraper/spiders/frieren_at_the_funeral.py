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
    allowed_domains = ['sousou-no-frieren.online', 'img.spoilerhat.com']
    
    # Initial chapter list (can be empty; will be populated from selector)
    chapter_list = [""]
    
    # CSS selector to extract chapter URLs from the main listing page
    chapter_list_selector = 'ul li a::attr(href)'
    
    # Regex pattern to extract chapter index from the URL
    chapter_pattern = r'chapter-(.+?)/'
    
    # Boolean to enable pagination logic (False if chapter_list_selector is used)
    paginate = False

    # URL to start crawling chapter list
    start_url = "https://sousou-no-frieren.online"
    
    # Starting index to control which chapter to begin scraping from
    start_chapter = 0

    # Template to build chapter URLs dynamically
    url_template = "https://sousou-no-frieren.online/manga/sousou-no-frieren-chapter-{chapter}/"
    
    # CSS selector to extract image elements from chapter pages
    image_selector = "img[id^='image-']"
    
    # List of image-host domains for filtering
    image_host_filters = allowed_domains

    # File extension for saved images
    file_ext = ".jpg"
