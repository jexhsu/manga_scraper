from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from manga_scraper.settings import (
    POSTGRESQL_DB,
    POSTGRESQL_USER,
    POSTGRESQL_PASSWORD,
    POSTGRESQL_HOST,
    POSTGRESQL_PORT,
)

DATABASE_URL = f"postgresql://{POSTGRESQL_USER}:{POSTGRESQL_PASSWORD}@{POSTGRESQL_HOST}:{POSTGRESQL_PORT}/{POSTGRESQL_DB}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
