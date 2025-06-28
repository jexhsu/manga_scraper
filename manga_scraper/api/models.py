import uuid
from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    DateTime,
    String,
    Integer,
    Float,
    ForeignKey,
    Text,
    func,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )  # UUID primary key with default uuid4
    username = Column(String, unique=True, nullable=False)  # Ensure username is unique
    password = Column(String, nullable=False)  # Hashed password
    is_admin = Column(Boolean, default=False)  # Only admins can register


class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(String, primary_key=True, index=True)  # Unique task UUID
    cmd = Column(Text, nullable=False)  # Command line used to start task
    status = Column(
        String, nullable=False, default="running"
    )  # running, finished, terminated, failed
    start_time = Column(
        DateTime(timezone=True), server_default=func.now()
    )  # Start timestamp
    end_time = Column(
        DateTime(timezone=True), nullable=True
    )  # End timestamp (nullable until finished)
    pid = Column(Integer, nullable=True)  # Process ID of running task (optional)
    is_admin_only = Column(Boolean, default=True)  # Only admins can manage this task


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
