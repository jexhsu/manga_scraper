from fastapi import FastAPI
from manga_scraper.api.controller.auth_routes import auth_router
from manga_scraper.api.controller.task_routes import task_router
from manga_scraper.api.controller.manga_routes import manga_router
from manga_scraper.api.controller.chapter_routes import chapter_router
from manga_scraper.api.controller.page_routes import page_router
from manga_scraper.settings import VERSION

app = FastAPI(
    title="Manga Scraper API",
    description="JWT Auth + Admin Crawler + Manga DB",
    openapi_tags=[{"name": "Auth", "description": "JWT Auth + Admin User Management"}],
    version=VERSION,
    docs_url=f"/api/{VERSION}/docs",
    redoc_url=f"/api/{VERSION}/redoc",
    contact={"email": "jexhsu@gmail.com"},
    swagger_ui_parameters={"persistAuthorization": True},
)


@app.on_event("startup")
async def on_startup():
    """
    This function runs on application startup.
    It will print the custom URL for the docs.
    """
    print(
        f"INFO: API documentation available at http://127.0.0.1:8000/api/{VERSION}/docs"
    )


# Include routers for authentication and API endpoints
app.include_router(auth_router, prefix=f"/api/{VERSION}/auth", tags=["Auth"])
app.include_router(task_router, prefix=f"/api/{VERSION}/tasks", tags=["Tasks"])
app.include_router(manga_router, prefix=f"/api/{VERSION}/mangas", tags=["Manga"])
app.include_router(chapter_router, prefix=f"/api/{VERSION}/mangas", tags=["Chapter"])
app.include_router(page_router, prefix=f"/api/{VERSION}/mangas", tags=["Page"])
