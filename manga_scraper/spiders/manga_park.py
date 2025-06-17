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

    allowed_domains = ["mangapark.io"]
    chapter_list_selector = "div.space-x-1 a::attr(href)"
    anti_scraping_url = True
    root_dir = "downloads/manga_park"
    use_playwright = True
    image_selector = "div[data-name='image-show'] img"

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        # Construct URL patterns based on manga ID
        self.chapter_pattern = rf"{self.manga_id}/(.+)"
        self.start_url = f"https://mangapark.io/title/{self.manga_id}"
        self.url_template = f"https://mangapark.io/title/{self.manga_id}/{{chapter}}/"


# Example of another manga spider
class AnotherMangaSpider(BaseMangaParkSpider):
    """
    Example of another manga spider using the same base configuration.
    Only manga ID and name need to be changed.
    """

    name = "another_manga"  # Unique spider name
    manga_id = "12345-en-another_manga"  # Different manga ID


class AgirlOnTheShoreSpider(BaseMangaParkSpider):
    """
    Example of another manga spider using the same base configuration.
    Only manga ID and name need to be changed.
    """

    name = "a_gril_on_the_shore"
    manga_id = "29929-en-a-girl-on-the-shore"  # Different manga ID


class GoodNightPunpunSpider(BaseMangaParkSpider):
    """
    Example of another manga spider using the same base configuration.
    Only manga ID and name need to be changed.
    """

    name = "good_night_punpun"
    manga_id = "18981-en-goodnight-punpun"  # Different manga ID


class NeonGenesisEvangelionSpider(BaseMangaParkSpider):
    """
    Example of another manga spider using the same base configuration.
    Only manga ID and name need to be changed.
    """

    name = "neon_genesis_evangelion"
    manga_id = "11218-en-neon-genesis-evangelion"  # Different manga ID
