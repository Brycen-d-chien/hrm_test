import os
from urllib.parse import quote_plus


SUPPORTED_DB_ENGINES = {"sqlite", "postgres"}


def get_database_url() -> str:
    """
    Priority:
    1. DATABASE_URL if set directly (production/staging)
    2. Build from DB_ENGINE + component variables
    3. Default: SQLite
    """
    database_url = os.getenv("DATABASE_URL", "").strip()
    if database_url:
        return database_url

    engine = get_db_engine()

    if engine == "postgres":
        host = os.getenv("POSTGRES_HOST", "localhost").strip()
        port = os.getenv("POSTGRES_PORT", "5432").strip()
        db = os.getenv("POSTGRES_DB", "hrm").strip()
        user = quote_plus(os.getenv("POSTGRES_USER", "postgres").strip())
        password = quote_plus(os.getenv("POSTGRES_PASSWORD", "postgres").strip())
        return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"

    sqlite_path = os.getenv("SQLITE_PATH", "./hrm.db").strip() or "./hrm.db"
    if sqlite_path == ":memory:":
        return "sqlite:///:memory:"
    normalized_sqlite_path = sqlite_path.replace("\\", "/")
    return f"sqlite:///{normalized_sqlite_path}"


def get_db_engine() -> str:
    engine = os.getenv("DB_ENGINE", "sqlite").strip().lower()
    if engine not in SUPPORTED_DB_ENGINES:
        raise ValueError(
            f"Unsupported DB_ENGINE '{engine}'. Supported values: {sorted(SUPPORTED_DB_ENGINES)}"
        )
    return engine


def is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


def should_auto_create_schema(url: str) -> bool:
    auto_create = os.getenv("AUTO_CREATE_SCHEMA", "").strip().lower()
    if auto_create in {"1", "true", "yes", "on"}:
        return True
    if auto_create in {"0", "false", "no", "off"}:
        return False
    return is_sqlite(url)
