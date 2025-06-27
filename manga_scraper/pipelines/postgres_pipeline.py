# pipelines/postgres_pipeline.py
import logging
import psycopg2
from psycopg2 import sql
from itemadapter import ItemAdapter
import re

logger = logging.getLogger(__name__)


class PostgreSQLPipeline:
    def __init__(self):
        self.conn = None
        self.cur = None
        self.tables_created = False

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        pipeline.crawler = crawler
        return pipeline

    def open_spider(self, spider):
        try:
            self.conn = psycopg2.connect(
                dbname=self.crawler.settings.get("POSTGRESQL_DB"),
                user=self.crawler.settings.get("POSTGRESQL_USER"),
                password=self.crawler.settings.get("POSTGRESQL_PASSWORD"),
                host=self.crawler.settings.get("POSTGRESQL_HOST"),
                port=self.crawler.settings.get("POSTGRESQL_PORT"),
            )
            self.conn.autocommit = False  # Enable transactions
            self.cur = self.conn.cursor()
            self._ensure_tables()
            logger.info("Connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

    def _ensure_tables(self):
        """Ensure all required tables exist with correct schema"""
        try:
            # Check if tables exist
            self.cur.execute(
                """
                SELECT EXISTS (
                    SELECT FROM pg_tables
                    WHERE schemaname = 'public' 
                    AND tablename = 'manga'
                )
            """
            )
            tables_exist = self.cur.fetchone()[0]

            if not tables_exist:
                self._create_tables()
                self.conn.commit()
                logger.info("Created database tables")
            else:
                self._migrate_tables()

            self.tables_created = True
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error ensuring tables exist: {e}")
            raise

    def _create_tables(self):
        """Create all required tables"""
        self.cur.execute(
            """
            CREATE TABLE manga (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT UNIQUE,
                follows INTEGER,
                total_chapters INTEGER DEFAULT 0
            )
        """
        )

        self.cur.execute(
            """
            CREATE TABLE search_keywords (
                keyword TEXT,
                manga_id TEXT REFERENCES manga(id),
                total_hits INTEGER,
                PRIMARY KEY (keyword, manga_id)
            )
        """
        )

        self.cur.execute(
            """
            CREATE TABLE chapters (
                id TEXT PRIMARY KEY,
                manga_id TEXT REFERENCES manga(id),
                number_name TEXT,
                text_name TEXT,
                full_name TEXT,
                url TEXT,
                order_index FLOAT,
                total_pages INTEGER DEFAULT 0
            )
        """
        )

        self.cur.execute(
            """
            CREATE TABLE pages (
                chapter_id TEXT REFERENCES chapters(id),
                page_number INTEGER,
                url TEXT,
                PRIMARY KEY (chapter_id, page_number)
            )
        """
        )

    def _migrate_tables(self):
        """Migrate existing tables if schema changes"""
        try:
            # Check if total_chapters column exists in manga table
            self.cur.execute(
                """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='manga' AND column_name='total_chapters'
            """
            )
            if not self.cur.fetchone():
                self.cur.execute(
                    "ALTER TABLE manga ADD COLUMN total_chapters INTEGER DEFAULT 0"
                )
                logger.info("Added total_chapters column to manga table")

            # Similarly check for other schema changes
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error migrating tables: {e}")
            raise

    def process_item(self, item, spider):
        if not self.tables_created:
            logger.error("Tables not created, skipping item processing")
            return item

        adapter = ItemAdapter(item)
        try:
            if adapter["item_type"] == "MangaItem":
                self._upsert_manga(adapter)
            elif adapter["item_type"] == "SearchKeywordMangaLinkItem":
                self._insert_search_keyword(adapter)
            elif adapter["item_type"] == "ChapterItem":
                self._upsert_chapter(adapter)
            elif adapter["item_type"] == "PageItem":
                self._insert_page(adapter)
            elif adapter["item_type"] == "MangaChapterLinkItem":
                self._update_manga_chapter_count(adapter)
            elif adapter["item_type"] == "ChapterPageLinkItem":
                self._update_chapter_page_count(adapter)

            return item
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error processing item {adapter['item_type']}: {e}")
            raise

    def _upsert_manga(self, item):
        query = """
            INSERT INTO manga (id, title, url, follows)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                follows = EXCLUDED.follows
        """
        self.cur.execute(
            query,
            (
                item["manga_id"],
                item["manga_name"],
                item["manga_url"],
                item.get("manga_follows"),
            ),
        )
        self.conn.commit()

    def _update_manga_chapter_count(self, item):
        query = """
            UPDATE manga 
            SET total_chapters = %s 
            WHERE id = %s
        """
        self.cur.execute(query, (item["total_chapters"], item["manga_id"]))
        self.conn.commit()

    def _upsert_chapter(self, item):
        query = """
            INSERT INTO chapters (
                id, manga_id, number_name, text_name, 
                full_name, url, order_index
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                text_name = EXCLUDED.text_name,
                full_name = EXCLUDED.full_name
        """
        self.cur.execute(
            query,
            (
                item["chapter_id"],
                item["manga_id"],
                item["chapter_number_name"],
                item.get("chapter_text_name"),
                item["chapter_name"],
                item["chapter_url"],
                self._parse_chapter_index(item["chapter_number_name"]),
            ),
        )
        self.conn.commit()

    def _update_chapter_page_count(self, item):
        query = """
            UPDATE chapters 
            SET total_pages = %s 
            WHERE id = %s
        """
        self.cur.execute(query, (item["total_pages"], item["chapter_id"]))
        self.conn.commit()

    def _insert_search_keyword(self, item):
        query = """
            INSERT INTO search_keywords (keyword, manga_id, total_hits)
            VALUES (%s, %s, %s)
            ON CONFLICT (keyword, manga_id) DO NOTHING
        """
        self.cur.execute(
            query, (item["keyword"], item["manga_id"], item["total_mangas"])
        )
        self.conn.commit()

    def _insert_page(self, item):
        query = """
            INSERT INTO pages (chapter_id, page_number, url)
            VALUES (%s, %s, %s)
            ON CONFLICT (chapter_id, page_number) DO NOTHING
        """
        self.cur.execute(
            query, (item["chapter_id"], item["page_number"], item["page_url"])
        )
        self.conn.commit()

    def _parse_chapter_index(self, chapter_str):
        try:
            numbers = re.findall(r"\d+\.?\d*", chapter_str)
            return float(numbers[0]) if numbers else 0.0
        except:
            return 0.0

    def close_spider(self, spider):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        logger.info("Closed PostgreSQL connection")
