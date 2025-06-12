from .base_spider import BaseMangaSpider

class demo_slayerSpider(BaseMangaSpider):
    name = "demo_slayer"
    site_name = "demo_slayer"
    allowed_domains = ['w3.demon-slayer.online', 'cdn.readkakegurui.com']

    chapter_list = [""]
    chapter_list_selector = 'li a::attr(href)'
    chapter_pattern = r'chapter-(.+?)/'
    start_url="https://w3.demon-slayer.online"
    start_chapter = 0

    url_template = "https://w3.demon-slayer.online/manga/demon-slayer-kimetsu-manga-chapter-{chapter}/"
    image_selector = "a img.aligncenter"
    image_attr = "src"
    image_host_filters = allowed_domains
    file_ext = ".jpg"
