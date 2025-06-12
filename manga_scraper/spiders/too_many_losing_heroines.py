from .base_spider import BaseMangaSpider

class too_many_losing_heroinesSpider(BaseMangaSpider):
    name = "too_many_losing_heroines"
    site_name = "too_many_losing_heroines"
    allowed_domains = ['toomanylosingheroines.com', 'pic.readkakegurui.com']

    chapter_list = [""]
    chapter_list_selector = 'div li a::attr(href)'
    chapter_pattern = r'chapter-(.+?)/'
    start_url="https://toomanylosingheroines.com"
    start_chapter = 0

    url_template = "https://toomanylosingheroines.com/manga/too-many-losing-heroines-chapter-{chapter}/"
    image_selector = "div img.aligncenter"
    image_attr = "src"
    image_host_filters = allowed_domains
    file_ext = ".webp"
