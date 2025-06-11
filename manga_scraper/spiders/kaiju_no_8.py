from .base_spider import BaseMangaSpider

class kaiju_no_8Spider(BaseMangaSpider):
    name = "kaiju_no_8"
    site_name = "kaiju_no_8"
    allowed_domains = ['kaiju-no8.com', 'cdn.black-clover.org']

    chapter_list = [""]
    chapter_list_selector = 'ul li a::attr(href)'
    chapter_pattern = r'chapter-(.+?)/'
    start_url = "https://kaiju-no8.com"

    url_template = "https://kaiju-no8.com/manga/kaiju-no-8-chapter-{chapter}/"
    image_selector = "img"
    image_attr = "src"
    image_host_filters = allowed_domains
    file_ext = ".webp"



    