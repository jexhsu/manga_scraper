# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

from scrapy import Spider


class BaseMangaSpider(Spider):
    def __init__(self, search_term="a girl on the shore", debug=False, **kwargs):
        super().__init__(**kwargs)
        self.search_term = search_term
        self.debug_mode = str(debug).lower() in ("true", "1", "yes")
