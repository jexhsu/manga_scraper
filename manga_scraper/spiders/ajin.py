from .base_spider import BaseMangaSpider

class AjinSpider(BaseMangaSpider):
    """
    Spider class to scrape manga chapters and images from 'Ajin Manga' website.
    Inherits from BaseMangaSpider for common functionality.
    """
    # Unique spider name used for CLI execution
    name = "ajin"
    
    # Internal identifier for the site
    site_name = "ajin"
    
    # Domains allowed for crawling and image hosting
    allowed_domains = ['w9.ajinmanga.online', 'blogger.googleusercontent.com']
    
    # Initial chapter list (can be empty; will be populated from selector)
    chapter_list = [""]
    
    # CSS selector to extract chapter URLs from the main listing page
    chapter_list_selector = '#ceo_latest_comics_widget-3 ul li a::attr(href)'
    
    # Regex pattern to extract chapter index from the URL
    chapter_pattern = r'chapter-(.+?)/'
    
    # Boolean to enable pagination logic (False if chapter_list_selector is used)
    paginate = False

    # URL to start crawling chapter list
    start_url = "https://w9.ajinmanga.online"
    
    # Starting index to control which chapter to begin scraping from
    start_chapter = 2

    # Template to build chapter URLs dynamically
    url_template = "https://w9.ajinmanga.online/manga/ajin-chapter-{chapter}/"
    
    # CSS selector to extract image elements from chapter pages
    image_selector = "img"
    
    # List of image-host domains for filtering
    image_host_filters = allowed_domains

    # File extension for saved images
    file_ext = ".jpg"
