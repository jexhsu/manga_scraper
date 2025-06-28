from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from manga_scraper.api.controller.auth_routes import get_current_user
from manga_scraper.api.database import SessionLocal
from manga_scraper.api.models import Page, User

# Create a router for page routes
page_router = APIRouter()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@page_router.get(
    "/{manga_id}/chapters/{chapter_id}/pages",
)
def get_pages_for_chapter(
    manga_id: str,
    chapter_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all pages for a chapter in a manga. Login required."""
    return db.query(Page).filter(Page.chapter_id == chapter_id).all()
