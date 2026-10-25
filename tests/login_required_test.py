"""Tests for the login_required decorator. The tutorial says: "Be sure to write tests for this on your own!"

Behaviour under test:
- A logged-out user cannot delete a post: 401, JSON {"status": 0, "message": "Please log in."},
  and the post is still in the database.
- A logged-in user can delete it: JSON status 1, and the post is gone from the database and the home page.
- Logging out takes the permission away again.
- Adding a post also needs a login (add_entry checks the session itself).
"""

import json

from project import models
from project.app import app, db
from tests.conftest import login, logout


def add_post(title="Keep me", text="unless you are logged in"):
    post = models.Post(title, text)
    db.session.add(post)
    db.session.commit()
    return post.id


def post_count():
    return db.session.query(models.Post).count()


def test_delete_when_logged_out_is_refused(client):
    post_id = add_post()
    rv = client.get(f"/delete/{post_id}")
    assert rv.status_code == 401
    assert json.loads(rv.data) == {"status": 0, "message": "Please log in."}
    assert post_count() == 1


def test_delete_when_logged_in_removes_the_post(client):
    post_id = add_post(title="Short-lived post")
    login(client, app.config["USERNAME"], app.config["PASSWORD"])
    rv = client.get(f"/delete/{post_id}")
    assert rv.status_code == 200
    assert json.loads(rv.data)["status"] == 1
    assert post_count() == 0
    assert b"Short-lived post" not in client.get("/").data


def test_delete_is_refused_again_after_logout(client):
    post_id = add_post()
    login(client, app.config["USERNAME"], app.config["PASSWORD"])
    logout(client)
    rv = client.get(f"/delete/{post_id}")
    assert rv.status_code == 401
    assert post_count() == 1


def test_wrong_password_does_not_grant_delete(client):
    post_id = add_post()
    login(client, app.config["USERNAME"], "wrong-password")
    rv = client.get(f"/delete/{post_id}")
    assert rv.status_code == 401
    assert post_count() == 1


def test_add_when_logged_out_is_refused(client):
    rv = client.post("/add", data=dict(title="Spam", text="should not be saved"))
    assert rv.status_code == 401
    assert post_count() == 0
