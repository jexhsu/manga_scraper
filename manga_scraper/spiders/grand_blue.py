from .base_spider import BaseMangaSpider

class grand_blueSpider(BaseMangaSpider):
    name = "grand_blue"
    site_name = "grand_blue"
    allowed_domains = ['w38.readgrandblue.com', 'eu2.contabostorage.com']

    chapter_list = [""]
    chapter_list_selector = 'div a::attr(href)'
    chapter_pattern = r'chapter-(.+?)/'
    start_url="https://w38.readgrandblue.com"
    start_chapter = 45

    url_template = "https://w38.readgrandblue.com/manga/grand-blue-chapter-{chapter}/"
    image_selector = "img"
    image_attr = "src"
    image_host_filters = allowed_domains
    file_ext = ".jpg"