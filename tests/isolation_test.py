"""Tests must never touch the real database (local flaskr.db or the Postgres database on Render)."""

from pathlib import Path

from project.app import app, db

BASE_DIR = Path(__file__).resolve().parent.parent


def test_tests_use_the_test_database(client):
    """The engine the tests talk to must point at test.db, not at flaskr.db or DATABASE_URL."""
    with app.app_context():
        assert Path(db.engine.url.database).resolve() == BASE_DIR / "test.db"


def test_real_database_is_not_dropped(client):
    """Running the test suite must leave the app's own database file alone."""
    real_db = BASE_DIR / "project" / "flaskr.db"
    with app.app_context():
        assert Path(db.engine.url.database).resolve() != real_db.resolve()
