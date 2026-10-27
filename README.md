# E444-F2026-PRA6: Flaskr, Test-Driven Development and Deployment

**Author:** Frank (Qingtao) Liu

**Live app:** https://flaskr-frank.onrender.com

This repository is based on the course tutorial https://github.com/shuruizUofT/flaskr-tdd, which is
adapted from https://github.com/mjhea0/flaskr-tdd (MIT License, see `LICENSE`). Flaskr is a small
blog: log in, post entries, search them, and delete them by clicking (deleting requires a login).

## Run it locally (Windows)

```
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
python create_db.py
flask --app project.app run
```

Open http://127.0.0.1:5000 and log in with `admin` / `admin`.

## Run the tests

```
python -m pytest -v
python -m flake8 --exclude env --ignore E402,E501 .
python -m black --exclude=env --check .
```

GitHub Actions (`.github/workflows/main.yml`) runs the same three commands on every push, on Python
3.10 and 3.12.

## The test suite (26 tests)

| File | What it checks | Written by |
|---|---|---|
| `tests/app_test.py` | Home page loads, the test database exists and starts empty, login and logout with right and wrong credentials, posting a message (title escaped, HTML allowed in text), deleting needs a login | Tutorial |
| `tests/search_test.py` | `/search/` without a query shows only the form; a query matches titles and text, ignoring case; non-matching posts are hidden; search works without logging in; each result carries its post id so click-to-delete works; the home page links to search | Me |
| `tests/login_required_test.py` | Deleting while logged out returns 401 with `{"status": 0, "message": "Please log in."}` and the post stays; deleting after login removes it from the database and the page; logging out, or a wrong password, takes the permission away; adding a post while logged out is refused | Me |
| `tests/isolation_test.py` | The tests use `test.db`, never the app's own database or the Render Postgres database | Me |
| `tests/database_url_test.py` | The `DATABASE_URL` from Render is turned into a URL SQLAlchemy accepts, with the `psycopg2` driver named explicitly; no URL falls back to local SQLite | Me |

`tests/conftest.py` holds the shared `client` fixture and the `login` / `logout` helpers.

## Test-driven changes (red, then green)

Each change below started with a failing test. The failing output is quoted as it appeared.

**1. The tests were wiping the real database.** The tutorial fixture set `SQLALCHEMY_DATABASE_URI`
inside the fixture, but Flask-SQLAlchemy creates its engine when `project/app.py` is imported, so
the setting came too late. The tests ran against `project/flaskr.db` and `db.drop_all()` deleted its
table. `test_database` only passed upstream because a `test.db` file had been committed by mistake.
Following the tutorial's Postgres step (set `DATABASE_URL` to the Render database, then run the
tests) would have dropped the deployed tables.

- Red: `isolation_test.py` failed with `assert ...\project\flaskr.db == ...\test.db`, and
  `test_database` failed with `assert False`. 3 failed, 5 passed.
- Fix: `tests/conftest.py` sets `DATABASE_URL` to `test.db` before importing the app.
- Green: 8 passed. Checked by hand as well: a post in `flaskr.db`, and a post in a database named by
  `DATABASE_URL`, both survive a full test run.

**2. Clicking a search result could not delete it.** `search.html` used `entry.post_id`, but the
`Post` model's column is `id`, so every result had an empty `<h2 id="">` and `main.js` requested
`/delete/`.

- Red: `test_search_result_carries_post_id_for_delete` failed. 1 failed, 19 passed.
- Fix: `entry.post_id` became `entry.id` in `project/templates/search.html`.
- Green: 20 passed.

**3. The app crashed on start when connected to Postgres.** A rehearsal of the Render build in a
Linux container with Python 3.12 and a real Postgres database failed with
`ModuleNotFoundError: No module named 'psycopg'`: with `requirements.txt` unpinned, the container
installed a newer SQLAlchemy whose default Postgres driver is `psycopg` 3, while this project installs
`psycopg2-binary`.

- Red: `database_url_test.py` failed with `cannot import name 'database_url'`.
- Fix: a `database_url()` function in `project/app.py` rewrites `postgres://` and `postgresql://` to
  `postgresql+psycopg2://`, and `requirements.txt` pins every package, including SQLAlchemy.
- Green: 26 passed, and the container started, served pages, and stored posts in Postgres.

**Making sure the tests can fail.** The search and login-required features already existed in the
tutorial code, so those tests passed on the first run. To show they really check something, I broke
the code on purpose, one change at a time, on a throwaway copy:

| Deliberate bug | Tests that failed |
|---|---|
| Remove `@login_required` from delete | 4, including 3 of mine |
| Search ignores the post text | `test_search_matches_text_not_only_title` |
| Search becomes case-sensitive | 3 search tests |
| `/add` no longer checks the login | `test_add_when_logged_out_is_refused` (only mine catches it) |
| Logout does not end the session | `test_delete_is_refused_again_after_logout` (only mine catches it) |

## Deployment on Render

| Setting | Value |
|---|---|
| Service type | Web Service, free instance |
| Branch | `main` |
| Build command | `pip install -r requirements.txt` |
| Start command | `python create_db.py && gunicorn project.app:app` |
| `PYTHON_VERSION` | `3.12.7` |
| `DATABASE_URL` | Internal Database URL of the Render Postgres database |

The start command creates the database tables before the server starts. `db.create_all()` only
creates tables that are missing, so it is safe on every restart, and the tables do not have to be
created from a local machine with the external database URL.

Known limits, kept as in the tutorial: the admin password and `SECRET_KEY` are hard-coded, delete is
a `GET` request, and deleting an id that does not exist still reports success.
