from .base_spider import BaseMangaSpider

class demo_slayerSpider(BaseMangaSpider):
    name = "demo_slayer"
    site_name = "demo_slayer"
    allowed_domains = ['www.demonslayerr.com', 'kimetsu-yaiba.online']

    chapter_list = [""]
    chapter_list_selector = 'div.d-flex a::attr(href)'
    chapter_pattern = r'/(\d+)$'
    paginate=True
    start_url="https://www.demonslayerr.com/demon-slayer/manga/chapters"
    start_chapter = 0

    url_template = "https://www.demonslayerr.com/demon-slayer/manga/chapters/{chapter}/"
    image_selector = "div img.w-100"
    image_attr = "src"
    image_host_filters = allowed_domains
    file_ext = ".jpg"
