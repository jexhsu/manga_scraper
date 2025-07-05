# manga_scraper/spiders/common/config.py
class ParserConfig:
    """Base configuration class for all parsers"""

    _site_configs = {}

    @classmethod
    def register_config(cls, config_name, config):
        cls._site_configs[config_name] = config

    @classmethod
    def get_config(cls, config_name):
        return cls._site_configs.get(config_name)


class MangaParserConfig(ParserConfig):
    """Manga page parser configuration"""

    @staticmethod
    def create_site_config(
        chapters_selector,
        chapter_id_extractor,
        chapter_number_extractor,
        chapter_text_extractor=lambda x: "",
        use_playwright=False,
        chapter_parser_config=None,  # Link to corresponding chapter parser config
    ):
        return {
            "chapters_selector": chapters_selector,
            "chapter_id_extractor": chapter_id_extractor,
            "chapter_number_extractor": chapter_number_extractor,
            "chapter_text_extractor": chapter_text_extractor,
            "use_playwright": use_playwright,
            "chapter_parser_config": chapter_parser_config,
        }


class ChapterParserConfig(ParserConfig):
    """Chapter page parser configuration"""

    @staticmethod
    def create_site_config(
        page_urls_selector=None, page_urls_extractor=None, async_cleanup=False
    ):
        return {
            "page_urls_selector": page_urls_selector,
            "page_urls_extractor": page_urls_extractor,
            "async_cleanup": async_cleanup,
        }
