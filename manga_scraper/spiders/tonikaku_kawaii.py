from .base_spider import BaseMangaSpider

class tonikaku_kawaiiSpider(BaseMangaSpider):
    name = "tonikaku_kawaii"
    site_name = "tonikaku_kawaii"
    allowed_domains = ['w3.tonikakukawaii.com', 'cdn.readkakegurui.com']

    chapter_list = [""]
    chapter_list_selector = 'li a::attr(href)'
    chapter_pattern = r'chapter-(.+?)/'
    start_url="https://w3.tonikakukawaii.com"
    start_chapter = 269

    url_template = "https://w3.tonikakukawaii.com/manga/tonikaku-kawaii-chapter-{chapter}/"
    image_selector = "div img.aligncenter"
    image_attr = "src"
    image_host_filters = allowed_domains
    file_ext = ".webp"
