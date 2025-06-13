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
    allowed_domains = ['w3.tonikakukawaii.com', 'cdn.readkakegurui.com']
    
    # Initial chapter list (can be empty; will be populated from selector)
    chapter_list = [""]
    
    # CSS selector to extract chapter URLs from the main listing page
    chapter_list_selector = 'li a::attr(href)'
    
    # Regex pattern to extract chapter index from the URL
    chapter_pattern = r'chapter-(.+?)/'
    
    # Boolean to enable pagination logic (False if chapter_list_selector is used)
    paginate = False

    # URL to start crawling chapter list
    start_url = "https://w3.tonikakukawaii.com"
    
    # Starting index to control which chapter to begin scraping from
    start_chapter = 0

    # Template to build chapter URLs dynamically
    url_template = "https://w3.tonikakukawaii.com/manga/tonikaku-cawaii-chapter-{chapter}/"
    
    # CSS selector to extract image elements from chapter pages
    image_selector = "div img.aligncenter"
    
    # List of image-host domains for filtering
    image_host_filters = allowed_domains

    # File extension for saved images
    file_ext = ".webp"
