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
        chapters_selector=None,
        chapter_id_extractor=None,
        chapter_number_extractor=None,
        chapter_text_extractor=lambda x: "",
        chapter_parser_config=None,  # Link to corresponding chapter parser config
    ):
        return {
            "chapters_selector": chapters_selector,
            "chapter_id_extractor": chapter_id_extractor,
            "chapter_number_extractor": chapter_number_extractor,
            "chapter_text_extractor": chapter_text_extractor,
            "chapter_parser_config": chapter_parser_config,
        }


class ChapterParserConfig(ParserConfig):
    """Chapter page parser configuration"""

    @staticmethod
    def create_site_config(content_key_selector=None, page_urls_extractor=None):
        return {
            "content_key_selector": content_key_selector,
            "page_urls_extractor": page_urls_extractor,
        }
