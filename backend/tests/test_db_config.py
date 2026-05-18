from unittest.mock import patch

import pytest

from backend.infrastructure.db_config import (
    get_database_url,
    get_db_engine,
    is_sqlite,
    should_auto_create_schema,
)


class TestGetDatabaseUrl:
    def test_prioritizes_direct_database_url(self):
        env = {"DATABASE_URL": "postgresql+psycopg://u:p@host/db"}
        with patch.dict("os.environ", env, clear=True):
            assert get_database_url() == "postgresql+psycopg://u:p@host/db"

    def test_builds_postgres_url_from_components(self):
        env = {
            "DB_ENGINE": "postgres",
            "POSTGRES_HOST": "myhost",
            "POSTGRES_PORT": "5432",
            "POSTGRES_DB": "hrm",
            "POSTGRES_USER": "admin",
            "POSTGRES_PASSWORD": "secret",
        }
        with patch.dict("os.environ", env, clear=True):
            url = get_database_url()
            assert url == "postgresql+psycopg://admin:secret@myhost:5432/hrm"

    def test_escapes_special_characters_in_postgres_credentials(self):
        env = {
            "DB_ENGINE": "postgres",
            "POSTGRES_USER": "admin+ops",
            "POSTGRES_PASSWORD": "p@ss:word/1",
        }
        with patch.dict("os.environ", env, clear=True):
            url = get_database_url()
            assert url == "postgresql+psycopg://admin%2Bops:p%40ss%3Aword%2F1@localhost:5432/hrm"

    def test_defaults_to_sqlite_when_no_env(self):
        with patch.dict("os.environ", {}, clear=True):
            url = get_database_url()
            assert url.startswith("sqlite:///")
            assert "hrm.db" in url

    def test_uses_custom_sqlite_path(self):
        with patch.dict("os.environ", {"SQLITE_PATH": "/tmp/test.db"}, clear=True):
            url = get_database_url()
            assert url == "sqlite:////tmp/test.db"

    def test_normalizes_windows_sqlite_path(self):
        with patch.dict("os.environ", {"SQLITE_PATH": r"D:\data\hrm.db"}, clear=True):
            url = get_database_url()
            assert url == "sqlite:///D:/data/hrm.db"

    def test_supports_in_memory_sqlite(self):
        with patch.dict("os.environ", {"SQLITE_PATH": ":memory:"}, clear=True):
            assert get_database_url() == "sqlite:///:memory:"

    def test_database_url_takes_priority_over_db_engine(self):
        env = {
            "DATABASE_URL": "postgresql+psycopg://direct/db",
            "DB_ENGINE": "postgres",
            "POSTGRES_HOST": "other",
        }
        with patch.dict("os.environ", env, clear=True):
            assert get_database_url() == "postgresql+psycopg://direct/db"


class TestGetDbEngine:
    def test_defaults_to_sqlite(self):
        with patch.dict("os.environ", {}, clear=True):
            assert get_db_engine() == "sqlite"

    def test_raises_for_unsupported_engine(self):
        with patch.dict("os.environ", {"DB_ENGINE": "postgre"}, clear=True):
            with pytest.raises(ValueError, match="Unsupported DB_ENGINE"):
                get_db_engine()


class TestIsSqlite:
    def test_true_for_sqlite_url(self):
        assert is_sqlite("sqlite:///./hrm.db") is True

    def test_false_for_postgres_url(self):
        assert is_sqlite("postgresql+psycopg://user:pass@host/db") is False

    def test_false_for_empty_string(self):
        assert is_sqlite("") is False


class TestShouldAutoCreateSchema:
    def test_defaults_true_for_sqlite(self):
        with patch.dict("os.environ", {}, clear=True):
            assert should_auto_create_schema("sqlite:///./hrm.db") is True

    def test_defaults_false_for_postgres(self):
        with patch.dict("os.environ", {}, clear=True):
            assert should_auto_create_schema("postgresql+psycopg://user:pass@host/db") is False

    def test_can_force_true(self):
        with patch.dict("os.environ", {"AUTO_CREATE_SCHEMA": "true"}, clear=True):
            assert should_auto_create_schema("postgresql+psycopg://user:pass@host/db") is True

    def test_can_force_false(self):
        with patch.dict("os.environ", {"AUTO_CREATE_SCHEMA": "false"}, clear=True):
            assert should_auto_create_schema("sqlite:///./hrm.db") is False
