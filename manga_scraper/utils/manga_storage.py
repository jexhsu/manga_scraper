# manga_scraper/utils/manga_storage.py
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional
import logging

from manga_scraper.utils.chapter_utils import extract_chapter_number
from manga_scraper.settings import DATABASE_NAME

DATABASE_PATH = Path(f"data/{DATABASE_NAME}.db")
logger = logging.getLogger(__name__)


class MangaDB:
    """SQLite storage for manga data with proper keyword-manga relationships."""

    def __init__(self, db_path: Path = DATABASE_PATH):
        """Initialize database with proper directory creation."""
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database tables with complete schema including relationship table."""
        with sqlite3.connect(str(self.db_path)) as conn:
            # Manga table (now with total_chapters)
            conn.execute(
                """
            CREATE TABLE IF NOT EXISTS manga (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT UNIQUE,
                follows INTEGER DEFAULT 0,
                total_chapters INTEGER DEFAULT 0
            )"""
            )

            # Manga-Keyword relationship table
            conn.execute(
                """
            CREATE TABLE IF NOT EXISTS manga_keywords (
                manga_id TEXT NOT NULL,
                keyword TEXT NOT NULL,
                PRIMARY KEY (manga_id, keyword),
                FOREIGN KEY (manga_id) REFERENCES manga(id)
            )"""
            )

            # Search keywords summary table
            conn.execute(
                """
            CREATE TABLE IF NOT EXISTS search_keywords (
                keyword TEXT PRIMARY KEY,
                manga_data TEXT NOT NULL,  -- JSON array of {id, url, follows}
                total_mangas INTEGER DEFAULT 0
            )"""
            )

            # Chapters table (now with total_pages)
            conn.execute(
                """
            CREATE TABLE IF NOT EXISTS chapters (
                id TEXT PRIMARY KEY,
                manga_id TEXT NOT NULL,
                name TEXT,
                number_name REAL NOT NULL,
                text_name TEXT,
                url TEXT UNIQUE,
                total_pages INTEGER DEFAULT 0,
                FOREIGN KEY (manga_id) REFERENCES manga(id)
            )"""
            )

            # Pages table (removed total_pages from here)
            conn.execute(
                """
            CREATE TABLE IF NOT EXISTS pages (
                chapter_id TEXT NOT NULL,
                number INTEGER NOT NULL,
                url TEXT NOT NULL,
                path TEXT,
                PRIMARY KEY (chapter_id, number),
                FOREIGN KEY (chapter_id) REFERENCES chapters(id)
            )"""
            )

            # Create indexes
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_chapters_manga ON chapters(manga_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_pages_chapter ON pages(chapter_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_manga_keywords ON manga_keywords(manga_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_keyword_mangas ON manga_keywords(keyword)"
            )

    def save_manga(self, data: List[Dict]):
        """Save scraped manga data with proper relationship handling."""
        with sqlite3.connect(str(self.db_path)) as conn:
            # First pass: Save all manga and chapter items
            for item in data:
                try:
                    if item["item_type"] == "MangaItem":
                        conn.execute(
                            "INSERT OR REPLACE INTO manga (id, title, url, follows) VALUES (?, ?, ?, ?)",
                            (
                                item["manga_id"],
                                item["manga_name"],
                                item["manga_url"],
                                int(item.get("manga_follows", ["0"])[0]),
                            ),
                        )

                    elif item["item_type"] == "ChapterItem":
                        conn.execute(
                            """
                            INSERT OR REPLACE INTO chapters 
                            (id, manga_id, name, number_name, text_name, url) 
                            VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            (
                                item["chapter_id"],
                                item["manga_id"],
                                item["chapter_name"],
                                extract_chapter_number(item["chapter_number_name"]),
                                item["chapter_text_name"],
                                item["chapter_url"],
                            ),
                        )

                    elif item["item_type"] == "PageItem":
                        conn.execute(
                            "INSERT OR REPLACE INTO pages (chapter_id, number, url) VALUES (?, ?, ?)",
                            (
                                item["chapter_id"],
                                item["page_number"],
                                item["page_url"],
                            ),
                        )

                except Exception as e:
                    logger.error(f"Error saving {item.get('item_type')}: {str(e)}")

            # Second pass: Handle relationships and summaries
            for item in data:
                try:
                    if item["item_type"] == "SearchKeywordMangaLinkItem":
                        # 1. Establish manga-keyword relationship
                        conn.execute(
                            "INSERT OR IGNORE INTO manga_keywords VALUES (?, ?)",
                            (item["manga_id"], item["keyword"]),
                        )

                        # 2. Update search keyword summary
                        cur = conn.execute(
                            """
                            SELECT m.id, m.url, m.follows 
                            FROM manga m
                            JOIN manga_keywords mk ON m.id = mk.manga_id
                            WHERE mk.keyword = ?
                        """,
                            (item["keyword"],),
                        )

                        manga_data = [
                            {"id": row[0], "url": row[1], "follows": row[2]}
                            for row in cur.fetchall()
                        ]

                        conn.execute(
                            "INSERT OR REPLACE INTO search_keywords VALUES (?, ?, ?)",
                            (
                                item["keyword"],
                                json.dumps(manga_data),
                                item["total_mangas"],
                            ),
                        )

                    elif item["item_type"] == "MangaChapterLinkItem":
                        # Update total chapters in manga table
                        conn.execute(
                            "UPDATE manga SET total_chapters = ? WHERE id = ?",
                            (item["total_chapters"], item["manga_id"]),
                        )

                    elif item["item_type"] == "ChapterPageLinkItem":
                        # Update total pages in chapters table
                        conn.execute(
                            "UPDATE chapters SET total_pages = ? WHERE id = ?",
                            (item["total_pages"], item["chapter_id"]),
                        )

                except Exception as e:
                    logger.error(
                        f"Error processing relationship {item.get('item_type')}: {str(e)}"
                    )

    def get_manga(self, manga_id: str) -> Optional[Dict]:
        """Get manga by ID."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cur = conn.execute("SELECT * FROM manga WHERE id = ?", (manga_id,))
            if row := cur.fetchone():
                return dict(
                    zip(["id", "title", "url", "follows", "total_chapters"], row)
                )
        return None

    def get_chapters(self, manga_id: str) -> List[Dict]:
        """Get all chapters for a manga."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cur = conn.execute(
                """
                SELECT * FROM chapters 
                WHERE manga_id = ? 
                ORDER BY number_name DESC
                """,
                (manga_id,),
            )
            columns = [
                "id",
                "manga_id",
                "name",
                "number_name",
                "text_name",
                "url",
                "total_pages",
            ]
            return [dict(zip(columns, row)) for row in cur.fetchall()]

    def get_pages(self, chapter_id: str) -> List[Dict]:
        """Get all pages for a chapter."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cur = conn.execute(
                """
                SELECT * FROM pages 
                WHERE chapter_id = ? 
                ORDER BY number
                """,
                (chapter_id,),
            )
            return [
                dict(zip(["chapter_id", "number", "url", "path"], row))
                for row in cur.fetchall()
            ]

    def get_keyword_data(self, keyword: str) -> Optional[Dict]:
        """Get search keyword with associated manga data."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cur = conn.execute(
                "SELECT * FROM search_keywords WHERE keyword = ?",
                (keyword,),
            )
            if row := cur.fetchone():
                return {
                    "keyword": row[0],
                    "manga_data": json.loads(row[1]),
                    "total_mangas": row[2],
                }
        return None

    def mark_downloaded(self, chapter_id: str, paths: List[str]):
        """Mark chapter pages as downloaded."""
        with sqlite3.connect(str(self.db_path)) as conn:
            for i, path in enumerate(paths, 1):
                conn.execute(
                    "UPDATE pages SET path = ? WHERE chapter_id = ? AND number = ?",
                    (path, chapter_id, i),
                )
