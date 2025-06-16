from .base_spider import BaseMangaSpider

class BaseMangaParkSpider(BaseMangaSpider):
    """
    Base spider class for MangaPark website with common configurations.
    Individual manga spiders should inherit from this and only change necessary parameters.
    """
    name = None  # Must be overridden by child classes
    abstract = True  # Prevents this from being registered as a spider

    @property
    def site_name(self):
        return self.name
    
    allowed_domains = ['mangapark.io']
    chapter_list_selector = 'div.space-x-1 a::attr(href)'
    paginate = False
    anti_scraping_url = True
    use_playwright = True
    image_selector = "div[data-name='image-show'] img"
    image_host_filters = allowed_domains
    file_ext = ".jpeg"

    def __init__(self, *args, start_chapter=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Construct URL patterns based on manga ID
        self.chapter_pattern = rf'{self.manga_id}/(.+)'
        self.start_url = f"https://mangapark.io/title/{self.manga_id}"
        self.url_template = f"https://mangapark.io/title/{self.manga_id}/{{chapter}}/"

        # Override start_chapter if passed from command line
        if start_chapter is not None:
            try:
                self.start_chapter = int(start_chapter)
            except ValueError:
                # Fallback to 0 if conversion fails
                self.start_chapter = 0

# Example of another manga spider
class AnotherMangaSpider(BaseMangaParkSpider):
    """
    Example of another manga spider using the same base configuration.
    Only manga ID and name need to be changed.
    """
    name = "manga_park_another_manga"  # Unique spider name
    manga_id = "12345-en-another_manga"  # Different manga ID
    start_chapter = 0  # Starting chapter

class BocchiTheRockSpider(BaseMangaParkSpider):
    """
    Spider for scraping 'Bocchi The Rock' manga from MangaPark.
    Only requires manga ID and starting chapter configuration.
    """
    name = "manga_park_bocchi_the_rock"  # Spider identifier
    manga_id = "76065-en-bocchi-the-rock"  # Unique manga identifier on the site
    start_chapter = 0  # First chapter to scrape

class AgirlOnTheShoreSpider(BaseMangaParkSpider):
    """
    Example of another manga spider using the same base configuration.
    Only manga ID and name need to be changed.
    """
    name="manga_park_a_gril_on_the_shore"
    manga_id = "29929-en-a-girl-on-the-shore"  # Different manga ID
    start_chapter = 0

class GoodNightPunpunSpider(BaseMangaParkSpider):
    """
    Example of another manga spider using the same base configuration.
    Only manga ID and name need to be changed.
    """
    name="manga_park_good_night_punpun"
    manga_id = "18981-en-goodnight-punpun"  # Different manga ID
    start_chapter = 0