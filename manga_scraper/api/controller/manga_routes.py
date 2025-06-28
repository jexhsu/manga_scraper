from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from manga_scraper.api.controller.auth_routes import get_current_user
from manga_scraper.api.database import SessionLocal
from manga_scraper.api.models import Chapter, Manga, SearchKeyword, User
from typing import List

# Create a router for manga routes
manga_router = APIRouter()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@manga_router.get(
    "/search",
)
def search_mangas(
    keyword: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search mangas by keyword. Login required."""
    keyword_matches = (
        db.query(SearchKeyword)
        .filter(SearchKeyword.keyword.ilike(f"{keyword}%"))
        .limit(50)
        .all()
    )
    manga_ids = [k.manga_id for k in keyword_matches]
    if not manga_ids:
        return []
    mangas = db.query(Manga).filter(Manga.id.in_(manga_ids)).all()
    return mangas


@manga_router.get(
    "/{manga_id}",
)
def get_manga_detail(
    manga_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get manga details by ID. Login required."""
    return db.query(Manga).filter(Manga.id == manga_id).first()
