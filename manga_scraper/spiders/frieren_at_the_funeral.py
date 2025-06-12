from .base_spider import BaseMangaSpider

class frieren_at_the_funeralSpider(BaseMangaSpider):
    name = "frieren_at_the_funeral"
    site_name = "frieren_at_the_funeral"
    allowed_domains = ['sousou-no-frieren.online', 'img.spoilerhat.com']

    chapter_list = [""]
    chapter_list_selector = 'ul li a::attr(href)'
    chapter_pattern = r'chapter-(.+?)/'
    start_url="https://sousou-no-frieren.online"
    start_chapter = 0

    url_template = "https://sousou-no-frieren.online/manga/sousou-no-frieren-chapter-{chapter}/"
    image_selector = "img[id^='image-']"
    image_attr = "src"
    image_host_filters = allowed_domains
    file_ext = ".jpg"
