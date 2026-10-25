"""Tests for turning the DATABASE_URL that Render provides into a URL SQLAlchemy can use.

Render (like Heroku before it) may hand out URLs that start with postgres:// , which SQLAlchemy 2 rejects.
Newer SQLAlchemy releases also pick the psycopg (v3) driver for a bare postgresql:// URL, but this
project installs psycopg2-binary, so the driver must be named explicitly or the app crashes on start.
"""

from project.app import database_url

LOCAL = "sqlite:///C:/somewhere/flaskr.db"


def test_no_database_url_falls_back_to_local_sqlite():
    assert database_url(None, LOCAL) == LOCAL


def test_empty_database_url_falls_back_to_local_sqlite():
    assert database_url("", LOCAL) == LOCAL


def test_postgres_scheme_is_rewritten_with_psycopg2_driver():
    url = "postgres://user:pw@dpg-abc123-a/flaskr"
    assert (
        database_url(url, LOCAL) == "postgresql+psycopg2://user:pw@dpg-abc123-a/flaskr"
    )


def test_postgresql_scheme_gets_explicit_psycopg2_driver():
    url = "postgresql://user:pw@dpg-abc123-a.oregon-postgres.render.com/flaskr"
    assert database_url(url, LOCAL) == (
        "postgresql+psycopg2://user:pw@dpg-abc123-a.oregon-postgres.render.com/flaskr"
    )


def test_url_that_already_names_a_driver_is_left_alone():
    url = "postgresql+psycopg2://user:pw@host/flaskr"
    assert database_url(url, LOCAL) == url


def test_sqlite_url_is_left_alone():
    url = "sqlite:////tmp/other.db"
    assert database_url(url, LOCAL) == url
