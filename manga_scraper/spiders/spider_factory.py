from .base_spider import BaseMangaSpider

def create_spider_class(
    name,
    domain,
    chapter_list_selector,
    chapter_pattern,
    url_path="manga",
    image_selector="img",
    paginate=False,
    url_template=None
):
    """
    Factory function to create manga spider classes with common patterns.
    Automatically generates start_url and url_template based on domain.
    """
    class_name = f"{name.title().replace('_', '')}Spider"
    
    # Generate manga name in URL format (replace underscores with hyphens)
    manga_url_name = name.replace('_', '-')
    
    # Default URL template if not provided
    if url_template is None:
        url_template = f"https://{domain}/{url_path}/{manga_url_name}-chapter-{{chapter}}/"
    
    attrs = {
        'name': name,
        'site_name': name,
        'allowed_domains': [domain],
        'chapter_list_selector': chapter_list_selector,
        'chapter_pattern': chapter_pattern,
        'start_url': f"https://{domain}",
        'url_template': url_template,
        'image_selector': image_selector,
        'paginate': paginate,
        '__doc__': f"Spider class to scrape manga chapters and images from '{name.replace('_', ' ').title()}' website."
    }
    
    return type(class_name, (BaseMangaSpider,), attrs)

# Spider definitions
AjinSpider = create_spider_class(
    name="ajin",
    domain="w9.ajinmanga.online",
    chapter_list_selector='#ceo_latest_comics_widget-3 ul li a::attr(href)',
    chapter_pattern=r'chapter-(.+?)/',
    image_selector="img"
)

TooManyLosingHeroinesSpider = create_spider_class(
    name="too_many_losing_heroines",
    domain="toomanylosingheroines.com",
    chapter_list_selector='div li a::attr(href)',
    chapter_pattern=r'chapter-(.+?)/',
    image_selector="div img.aligncenter"
)

DemonSlayerSpider = create_spider_class(
    name="demon_slayer",
    domain="www.demonslayerr.com",
    chapter_list_selector='div.d-flex a::attr(href)',
    chapter_pattern=r'/(\d+)$',
    url_path="demon-slayer/manga/chapters",
    url_template="https://www.demonslayerr.com/demon-slayer/manga/chapters/{chapter}/",
    image_selector="div img.w-100",
    paginate=True
)

KaijuNo8Spider = create_spider_class(
    name="kaiju_no_8",
    domain="kaiju-no8.com",
    chapter_list_selector='ul li a::attr(href)',
    chapter_pattern=r'chapter-(.+?)/'
)

FrierenAtTheFuneralSpider = create_spider_class(
    name="frieren_at_the_funeral",
    domain="sousou-no-frieren.online",
    chapter_list_selector='ul li a::attr(href)',
    chapter_pattern=r'chapter-(.+?)/',
    image_selector="img[id^='image-']"
)

TonikakuKawaiiSpider = create_spider_class(
    name="tonikaku_kawaii",
    domain="w3.tonikakukawaii.com",
    chapter_list_selector='li a::attr(href)',
    chapter_pattern=r'chapter-(.+?)/',
    url_path="manga/tonikaku-cawaii", 
    image_selector="div img.aligncenter"
)

TokyoGhoulSpider = create_spider_class(
    name="tokyo_ghoul",
    domain="tgmanga.com",
    chapter_list_selector='li a::attr(href)',
    chapter_pattern=r'chapter-(.+?)/',
    image_selector="img.lazyloaded, img.alignnone, img.aligncenter"
)

SpyXFamilySpider = create_spider_class(
    name="spy_x_family",
    domain="w2.spyxfamilyseason.com",
    chapter_list_selector='#ceo_latest_comics_widget-3 ul li a::attr(href)',
    chapter_pattern=r'chapter-(.+?)/',
    image_selector="img"
)

GrandBlueSpider = create_spider_class(
    name="grand_blue",
    domain="w38.readgrandblue.com",
    chapter_list_selector='div a::attr(href)',
    chapter_pattern=r'chapter-(.+?)/',
    image_selector="img"
)

DarkGatheringSpider = create_spider_class(
    name="dark_gathering",
    domain="dark-gathering.com",
    chapter_list_selector='#ceo_latest_comics_widget-3 ul li a::attr(href)',
    chapter_pattern=r'chapter-(.+?)/',
    image_selector="img"
)

DandadanSpider = create_spider_class(
    name="dandadan",
    domain="dandadan.net",
    chapter_list_selector='ul li a::attr(href)',
    chapter_pattern=r'chapter-(.+?)/',
    image_selector="img"
)

BocchitheRockSpider = create_spider_class(
    name="bocchi_the_rock",
    domain="w3.bocchitherockmanga.com",
    chapter_list_selector='ul li a::attr(href)',
    chapter_pattern=r'chapter-(.+?)/',
    url_path="manga1/bocchi-the-rock",  # Custom URL path
    image_selector="div img.aligncenter"
)
