from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.infrastructure.db_config import get_database_url, is_sqlite

DATABASE_URL = get_database_url()

_engine_kwargs = {}
if is_sqlite(DATABASE_URL):
    # check_same_thread is SQLite-only and must not be passed to Postgres.
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
