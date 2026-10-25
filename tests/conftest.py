import os
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
TEST_DB = "test.db"

# project/app.py builds the database engine from DATABASE_URL the moment it is imported,
# so changing app.config inside the fixture is too late. Point DATABASE_URL at test.db
# BEFORE importing the app. This also overrides a DATABASE_URL left in the shell from the
# Render setup, so running the tests can never drop the tables of the deployed database.
os.environ["DATABASE_URL"] = f"sqlite:///{BASE_DIR.joinpath(TEST_DB)}"

from project.app import app, db  # noqa: E402  (must come after DATABASE_URL is set)


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()  # setup
        yield app.test_client()  # tests run here
        db.drop_all()  # teardown


def login(client, username, password):
    """Login helper function"""
    return client.post(
        "/login",
        data=dict(username=username, password=password),
        follow_redirects=True,
    )


def logout(client):
    """Logout helper function"""
    return client.get("/logout", follow_redirects=True)
