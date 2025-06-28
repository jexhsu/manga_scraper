from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from manga_scraper.api.controller.auth_routes import get_current_user
from manga_scraper.api.database import SessionLocal
from manga_scraper.api.models import Chapter, User

# Create a router for chapter routes
chapter_router = APIRouter()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@chapter_router.get(
    "/{manga_id}/chapters",
)
def get_chapters_for_manga(
    manga_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all chapters for a manga. Login required."""
    return db.query(Chapter).filter(Chapter.manga_id == manga_id).all()
