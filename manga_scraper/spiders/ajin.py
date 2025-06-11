from .base_spider import BaseMangaSpider

class AjinSpider(BaseMangaSpider):
    name = "ajin"
    site_name = "ajin"
    allowed_domains = ['w9.ajinmanga.online', 'blogger.googleusercontent.com']
    
    chapter_list = [""]
    chapter_list_selector = '#ceo_latest_comics_widget-3 ul li a::attr(href)'
    chapter_pattern = r'chapter-(.+?)/'
    start_url = "https://w9.ajinmanga.online"

    url_template = "https://w9.ajinmanga.online/manga/ajin-chapter-{chapter}/"
    image_selector = "img"
    image_attr = "src"
    image_host_filters = allowed_domains
    file_ext = ".jpg"