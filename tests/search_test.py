"""Tests for the search page (/search/). The tutorial says: "Be sure to write a test for this on your own!"

Behaviour under test:
- /search/ without a query shows the search form and no posts.
- With ?query=..., a post is listed when the query appears in its title OR its text, ignoring case.
- Posts that do not match are not listed.
- Search works without logging in.
- Each listed post carries its database id, so clicking it can delete the right post (static/main.js).
"""

from project import models
from project.app import db


def add_post(title, text):
    """Insert a post directly into the test database and return it."""
    post = models.Post(title, text)
    db.session.add(post)
    db.session.commit()
    return post


def test_search_page_without_query_shows_form_and_no_posts(client):
    add_post("Flask tips", "Use blueprints")
    rv = client.get("/search/")
    assert rv.status_code == 200
    assert b'name="query"' in rv.data
    assert b'class="entry"' not in rv.data


def test_search_matches_title_ignoring_case(client):
    add_post("Flask Tips", "Use blueprints")
    add_post("Cooking", "Boil the pasta")
    rv = client.get("/search/?query=flask")
    assert b"Flask Tips" in rv.data
    assert b"Cooking" not in rv.data


def test_search_matches_text_not_only_title(client):
    add_post("Weekend", "We went hiking near Toronto")
    add_post("Weekday", "Lectures all day")
    rv = client.get("/search/?query=TORONTO")
    assert b"Weekend" in rv.data
    assert b"Weekday" not in rv.data


def test_search_with_no_match_lists_nothing(client):
    add_post("Flask tips", "Use blueprints")
    rv = client.get("/search/?query=zzzz")
    assert rv.status_code == 200
    assert b'class="entry"' not in rv.data


def test_search_does_not_require_login(client):
    add_post("Public post", "Anyone can find this")
    rv = client.get("/search/?query=public")
    assert rv.status_code == 200
    assert b"Public post" in rv.data


def test_search_result_carries_post_id_for_delete(client):
    """main.js reads the <h2 id> of a clicked post and calls /delete/<id>; an empty id breaks delete."""
    post = add_post("Delete me", "from the search page")
    rv = client.get("/search/?query=delete")
    assert f'<h2 id="{post.id}">'.encode() in rv.data


def test_home_page_links_to_search(client):
    rv = client.get("/")
    assert b'href="/search/"' in rv.data
