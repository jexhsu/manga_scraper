from .base_spider import BaseMangaSpider

class bocchi_the_rockSpider(BaseMangaSpider):
    name = "bocchi_the_rock"
    site_name = "bocchi_the_rock"
    allowed_domains = ['w3.bocchitherockmanga.com', 'blogger.googleusercontent.com']
    
    chapter_list = [""]
    chapter_list_selector = 'ul li a::attr(href)'
    chapter_pattern = r'chapter-(.+?)/'
    start_url = "https://w3.bocchitherockmanga.com"
    start_chapter = 51

    url_template = "https://w3.bocchitherockmanga.com/manga1/bocchi-the-rock-chapter-{chapter}/"
    image_selector = "div img.aligncenter"
    image_attr = "src"
    image_host_filters = allowed_domains
    file_ext = ".webp"