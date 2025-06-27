from fastapi.encoders import jsonable_encoder
from typing import Literal, Optional
from fastapi import APIRouter, Form, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Manga, Chapter, Page, SearchKeyword
import subprocess

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/tasks/dispatch", tags=["Tasks"])
def dispatch_crawl_task(
    mode: Literal[
        "search_all", "search_only", "chapters_only", "chapters_select"
    ] = Form(
        ...,
        description="Crawl mode: search_all, search_only, chapters_only, or chapters_select",
    ),
    search_term: Optional[str] = Form(
        None, description="Keyword for manga search (required for search_* modes)"
    ),
    manga_id: Optional[str] = Form(
        None, description="Manga ID (required for chapters_* modes)"
    ),
    chapter_ids: Optional[str] = Form(
        None,
        description="Comma-separated chapter ID list (only required for chapters_select mode)",
    ),
    db: Session = Depends(get_db),
):
    """
    Dispatch a scraping task based on the selected mode:
    - `search_all`: search manga + all chapters + pages
    - `search_only`: search manga list only
    - `chapters_only`: get all chapters for a manga (no pages)
    - `chapters_select`: get selected chapters + pages
    """
    if mode in ["search_all", "search_only"]:
        if not search_term:
            raise HTTPException(
                status_code=400, detail="Missing search_term for search mode."
            )
    elif mode in ["chapters_only", "chapters_select"]:
        if not manga_id:
            raise HTTPException(
                status_code=400, detail="Missing manga_id for chapter mode."
            )
        if mode == "chapters_select" and not chapter_ids:
            raise HTTPException(
                status_code=400, detail="Missing chapter_ids for chapters_select mode."
            )

    cmd = ["scrapy", "crawl", "manga_park", "-a", f"mode={mode}"]

    if mode in ["search_all", "search_only"]:
        cmd += ["-a", f"search_term={search_term}"]
    else:
        cmd += ["-a", f"manga_id={manga_id}"]
        if mode == "chapters_select":
            cmd += ["-a", f"chapter_ids={chapter_ids}"]

    subprocess.Popen(cmd)

    response = {
        "status": "started",
        "mode": mode,
        "search_term": search_term,
        "manga_id": manga_id,
        "chapter_ids": chapter_ids.split(",") if chapter_ids else None,
    }

    # Query DB for search_only mode: return manga list matching search_term
    if mode == "search_only":
        # Step 1: Match keyword prefix from SearchKeyword table
        keyword_matches = (
            db.query(SearchKeyword)
            .filter(SearchKeyword.keyword.ilike(f"{search_term}%"))  # prefix matching
            .order_by(SearchKeyword.total_hits.desc())
            .limit(50)
            .all()
        )

        # Step 2: Extract matching manga IDs
        manga_ids = [k.manga_id for k in keyword_matches]

        # Step 3: Query Manga table for those IDs
        if manga_ids:
            mangas = (
                db.query(Manga)
                .filter(Manga.id.in_(manga_ids))
                .order_by(Manga.follows.desc())
                .all()
            )
            response["manga_list"] = jsonable_encoder(mangas)
        else:
            response["manga_list"] = []

    # Query DB for chapters_only mode: return all chapters for manga_id
    elif mode == "chapters_only":
        chapters = (
            db.query(Chapter)
            .filter(Chapter.manga_id == manga_id)
            .order_by(Chapter.order_index.asc())
            .all()
        )
        response["chapter_list"] = jsonable_encoder(chapters)

    return response


@router.get("/mangas/search", tags=["Manga"])
def search_mangas(
    keyword: str = Query(
        ..., description="Keyword to search manga via SearchKeyword (prefix match)"
    ),
    db: Session = Depends(get_db),
):
    """
    Search mangas in the database using keyword prefix matching on SearchKeyword table.
    Returns list of matched manga entries sorted by follows.
    """
    # Step 1: Match keyword prefix in SearchKeyword table
    keyword_matches = (
        db.query(SearchKeyword)
        .filter(SearchKeyword.keyword.ilike(f"{keyword}%"))  # prefix match
        .order_by(SearchKeyword.total_hits.desc())
        .limit(50)
        .all()
    )

    # Step 2: Extract manga IDs from matched entries
    manga_ids = [k.manga_id for k in keyword_matches]

    # Step 3: Query Manga table using those IDs
    if not manga_ids:
        return []

    mangas = (
        db.query(Manga)
        .filter(Manga.id.in_(manga_ids))
        .order_by(Manga.follows.desc())
        .all()
    )

    return mangas


@router.get("/mangas/{manga_id}", tags=["Manga"])
def get_manga_detail(manga_id: str, db: Session = Depends(get_db)):
    """
    Get full detail of a manga by its manga_id.
    """
    return db.query(Manga).filter(Manga.id == manga_id).first()


@router.get("/mangas/{manga_id}/chapters", tags=["Chapter"])
def get_chapters_for_manga(manga_id: str, db: Session = Depends(get_db)):
    """
    Get all chapters associated with a given manga_id.
    """
    return db.query(Chapter).filter(Chapter.manga_id == manga_id).all()


@router.get("/chapters/{chapter_id}/pages", tags=["Page"])
def get_pages_for_chapter(chapter_id: str, db: Session = Depends(get_db)):
    """
    Get all page image URLs for a specific chapter_id.
    """
    return db.query(Page).filter(Page.chapter_id == chapter_id).all()
