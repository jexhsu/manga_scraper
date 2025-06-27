from fastapi import FastAPI
from .controllers import router

app = FastAPI(title="Manga Scraper API")

app.include_router(router, prefix="/api")
