from .base_spider import BaseMangaSpider

class DandadanSpider(BaseMangaSpider):
    name = "dandadan"
    site_name = "dandadan"
    allowed_domains = [
        'dandadan.net',
        'cdn.readkakegurui.com',
        'pic.readkakegurui.com',
        'cdn.black-clover.org'
    ]
    
    chapter_list = [""]
    chapter_list_selector = 'ul li a::attr(href)'
    chapter_pattern = r'chapter-(.+?)/'
    start_url = "https://dandadan.net"

    url_template = "https://dandadan.net/manga/dandadan-chapter-{chapter}/"
    image_selector = "img"
    image_attr = "data-lazy-src"
    image_host_filters = allowed_domains  # use allowed_domains as filters here
    file_ext = ".webp"