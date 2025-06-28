from fastapi import APIRouter, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from manga_scraper.utils.task_manager import (
    start_async_scrapy_task,
    get_task_status,
    stop_task,
    list_all_tasks,
)
from manga_scraper.api.controller.auth_routes import get_current_user
from manga_scraper.api.database import SessionLocal
from manga_scraper.api.models import User
from typing import Literal, Optional

# Create a router for task routes
task_router = APIRouter()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@task_router.post(
    "/dispatch",
)
def dispatch_crawl_task(
    mode: Literal[
        "search_all", "search_only", "chapters_only", "chapters_select"
    ] = Form(...),
    search_term: Optional[str] = Form(None),
    manga_id: Optional[str] = Form(None),
    chapter_ids: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Dispatch a scraping task based on the selected mode:
    - `search_all`: search manga + all chapters + pages
    - `search_only`: search manga list only
    - `chapters_only`: get all chapters for a manga (no pages)
    - `chapters_select`: get selected chapters + pages
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can dispatch tasks.")

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

    task_id = start_async_scrapy_task(db, cmd)

    response = {
        "status": "started",
        "mode": mode,
        "search_term": search_term,
        "manga_id": manga_id,
        "chapter_ids": chapter_ids.split(",") if chapter_ids else None,
        "task_id": task_id,
    }

    return response


@task_router.get(
    "/status/{task_id}",
)
def check_task_status(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check the status of a task by its ID. Admins only."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403, detail="Only admins can check task status."
        )
    return get_task_status(db, task_id)


@task_router.get(
    "/list",
)
def list_tasks(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """List all tasks with their statuses. Admins only."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can list tasks.")
    return list_all_tasks(db)


@task_router.post(
    "/stop/{task_id}",
)
def stop_task_api(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Stop a running task by task_id. Admins only."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can stop tasks.")
    success = stop_task(db, task_id)
    if not success:
        raise HTTPException(
            status_code=404, detail="Task not found or already finished."
        )
    return {"message": "Task terminated."}
