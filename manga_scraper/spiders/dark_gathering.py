from .base_spider import BaseMangaSpider
class DarkGatheringSpider(BaseMangaSpider):
    name = "dark_gathering"
    site_name = "dark_gathering"
    allowed_domains = ['dark-gathering.com', 'blogger.googleusercontent.com']

    chapter_list = [""]
    chapter_list_selector = '#ceo_latest_comics_widget-3 ul li a::attr(href)'
    chapter_pattern = r'chapter-(.+?)/'
    start_url = "https://dark-gathering.com"

    url_template = "https://dark-gathering.com/manga/dark-gathering-chapter-{chapter}/"
    image_selector = "img"
    image_attr = "src"
    image_host_filters = allowed_domains
    file_ext = ".jpg"