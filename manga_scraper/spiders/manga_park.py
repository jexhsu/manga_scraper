# manga_scraper/spiders/manga_park.py
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


class AttackOnTitanSpider(BaseMangaParkSpider):
    """Spider for attack on titan manga."""

    name = "attack_on_titan"
    manga_id = "11643-en-attack-on-titan"


class GoodnightPunpunSpider(BaseMangaParkSpider):
    """Spider for goodnight punpun manga."""

    name = "goodnight_punpun"
    manga_id = "18981-en-goodnight-punpun"


class AGirlOnTheShoreSpider(BaseMangaParkSpider):
    """Spider for a girl on the shore manga."""

    name = "a_girl_on_the_shore"
    manga_id = "29929-en-a-girl-on-the-shore"


class NeonGenesisEvangelionSpider(BaseMangaParkSpider):
    name = "neon_genesis_evangelion"
    manga_id = "11218-en-neon-genesis-evangelion"  # Different manga ID

class MyWifeHasNoEmotionSpider(BaseMangaParkSpider):
    """Spider for my wife has no emotion manga."""
    name = "my_wife_has_no_emotion"
    manga_id = "77475-en-my-wife-has-no-emotion"
