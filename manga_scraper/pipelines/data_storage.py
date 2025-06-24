# manga_scraper/pipelines.py
from manga_scraper.utils.manga_storage import MangaDB
import logging

logger = logging.getLogger(__name__)


class MangaStoragePipeline:
    """Pipeline that saves scraped manga data to SQLite database when spider closes."""

    def __init__(self):
        """Initialize the database connection."""
        self.db = MangaDB()
        self.items = []  # Temporary storage for items before saving

    def process_item(self, item, spider):
        """Process each item by adding it to temporary storage.

        Args:
            item (dict): The scraped item
            spider (scrapy.Spider): The spider that scraped the item

        Returns:
            dict: The original item (unchanged)
        """
        self.items.append(dict(item))
        return item

    def close_spider(self, spider):
        """Called when the spider closes - saves all collected items to database.

        Args:
            spider (scrapy.Scrapy): The spider instance that's closing
        """
        try:
            logger.info(f"Saving {len(self.items)} items to database")
            self.db.save_manga(self.items)
            logger.info("Database save completed successfully")
        except Exception as e:
            logger.error(f"Error saving items to database: {str(e)}")
            # You might want to implement error recovery here
            raise
        finally:
            # Clear the temporary storage
            self.items = []
