from .base_spider import BaseMangaSpider

class DarkGatheringSpider(BaseMangaSpider):
    """
    Spider class to scrape manga chapters and images from 'Dark Gathering' website.
    Inherits from BaseMangaSpider for common functionality.
    """
    # Unique spider name used for CLI execution
    name = "dark_gathering"
    
    # Internal identifier for the site
    site_name = "dark_gathering"
    
    # Domains allowed for crawling and image hosting
    allowed_domains = ['dark-gathering.com', 'blogger.googleusercontent.com']
    
    # Initial chapter list (can be empty; will be populated from selector)
    chapter_list = [""]
    
    # CSS selector to extract chapter URLs from the main listing page
    chapter_list_selector = '#ceo_latest_comics_widget-3 ul li a::attr(href)'
    
    # Regex pattern to extract chapter index from the URL
    chapter_pattern = r'chapter-(.+?)/'
    
    # Boolean to enable pagination logic (False if chapter_list_selector is used)
    paginate = False

    # URL to start crawling chapter list
    start_url = "https://dark-gathering.com"
    
    # Starting index to control which chapter to begin scraping from
    start_chapter = 0

    # Template to build chapter URLs dynamically
    url_template = "https://dark-gathering.com/manga/dark-gathering-chapter-{chapter}/"
    
    # CSS selector to extract image elements from chapter pages
    image_selector = "img"
    
    # List of image-host domains for filtering
    image_host_filters = allowed_domains

    # File extension for saved images
    file_ext = ".jpg"
