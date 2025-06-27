from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Manga(Base):
    __tablename__ = "manga"
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, unique=True)
    follows = Column(Integer)
    total_chapters = Column(Integer, default=0)


class Chapter(Base):
    __tablename__ = "chapters"
    id = Column(String, primary_key=True)
    manga_id = Column(String, ForeignKey("manga.id"))
    number_name = Column(String)
    text_name = Column(String)
    full_name = Column(String)
    url = Column(String)
    order_index = Column(Float)
    total_pages = Column(Integer, default=0)


class Page(Base):
    __tablename__ = "pages"
    chapter_id = Column(String, ForeignKey("chapters.id"), primary_key=True)
    page_number = Column(Integer, primary_key=True)
    url = Column(String)


class SearchKeyword(Base):
    __tablename__ = "search_keywords"
    keyword = Column(String, primary_key=True)
    manga_id = Column(String, ForeignKey("manga.id"), primary_key=True)
    total_hits = Column(Integer)
