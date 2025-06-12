from .base_spider import BaseMangaSpider

class spy_x_familySpider(BaseMangaSpider):
    name = "spy_x_family"
    site_name = "spy_x_family"
    allowed_domains = ['w2.spyxfamilyseason.com', 'www.mangaread.org']

    chapter_list = [""]
    chapter_list_selector = '#ceo_latest_comics_widget-3 ul li a::attr(href)'
    chapter_pattern = r'chapter-(.+?)/'
    start_url="https://w2.spyxfamilyseason.com"
    start_chapter = 95

    url_template = "https://w2.spyxfamilyseason.com/manga/spy-x-family-chapter-{chapter}/"
    image_selector = "img"
    image_attr = "src"
    image_host_filters = allowed_domains
    file_ext = ".jpeg"