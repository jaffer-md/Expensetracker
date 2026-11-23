import sqlite3

import database.db as dbm
from database.queries import insert_expense


def login(client):
    client.post("/login", data=dict(email="demo@spendly.com", password="demo123"))


def valid_form(**overrides):
    data = dict(amount="50.0", category="Food", date="2026-03-20", description="Lunch")
    data.update(overrides)
    return data


def rows_for(temp_db, user_id=1):
    conn = sqlite3.connect(str(temp_db))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM expenses WHERE user_id = ? ORDER BY id", (user_id,)
    ).fetchall()
    conn.close()
    return rows


# ---------------------------- insert_expense --------------------------- #

def test_insert_expense_stores_row(temp_db):
    new_id = insert_expense(1, 50.0, "Food", "2026-03-20", "Lunch")
    row = [r for r in rows_for(temp_db) if r["id"] == new_id][0]
    assert row["amount"] == 50.0
    assert row["category"] == "Food"
    assert row["date"] == "2026-03-20"
    assert row["description"] == "Lunch"


def test_insert_expense_null_description(temp_db):
    new_id = insert_expense(1, 12.0, "Other", "2026-03-20", None)
    row = [r for r in rows_for(temp_db) if r["id"] == new_id][0]
    assert row["description"] is None


# ------------------------------ routes -------------------------------- #

def test_get_requires_login(client):
    r = client.get("/expenses/add")
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/login")


def test_post_requires_login(client, temp_db):
    before = len(rows_for(temp_db))
    r = client.post("/expenses/add", data=valid_form())
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/login")
    assert len(rows_for(temp_db)) == before


def test_get_form_has_seven_categories_and_post_method(client):
    login(client)
    r = client.get("/expenses/add")
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert 'method="POST"' in html
    for name in ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]:
        assert f'<option value="{name}"' in html
    assert html.count("<option ") == 7


def test_valid_post_inserts_and_redirects(client, temp_db):
    login(client)
    before = len(rows_for(temp_db))
    r = client.post("/expenses/add", data=valid_form())
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/profile")
    rows = rows_for(temp_db)
    assert len(rows) == before + 1
    assert rows[-1]["description"] == "Lunch"
    assert rows[-1]["amount"] == 50.0


def test_profile_lists_new_expense(client):
    login(client)
    client.post("/expenses/add", data=valid_form(description="Brand new thing"))
    html = client.get("/profile").get_data(as_text=True)
    assert "Brand new thing" in html


def _assert_rejected(client, temp_db, **overrides):
    login(client)
    before = len(rows_for(temp_db))
    data = valid_form(**overrides)
    r = client.post("/expenses/add", data=data)
    assert r.status_code == 200
    assert b"auth-error" in r.data
    assert len(rows_for(temp_db)) == before
    return r


def test_missing_amount(client, temp_db):
    _assert_rejected(client, temp_db, amount="")


def test_zero_amount(client, temp_db):
    _assert_rejected(client, temp_db, amount="0")


def test_negative_amount(client, temp_db):
    _assert_rejected(client, temp_db, amount="-5")


def test_non_numeric_amount(client, temp_db):
    _assert_rejected(client, temp_db, amount="abc")


def test_infinite_amount(client, temp_db):
    _assert_rejected(client, temp_db, amount="inf")


def test_nan_amount(client, temp_db):
    _assert_rejected(client, temp_db, amount="nan")


def test_invalid_category(client, temp_db):
    _assert_rejected(client, temp_db, category="Gadgets")


def test_invalid_date(client, temp_db):
    _assert_rejected(client, temp_db, date="2026-02-30")


def test_description_too_long(client, temp_db):
    _assert_rejected(client, temp_db, description="x" * 201)


def test_rejection_keeps_submitted_values(client, temp_db):
    r = _assert_rejected(client, temp_db, amount="0", description="Keep me")
    html = r.get_data(as_text=True)
    assert "Keep me" in html
    assert 'value="2026-03-20"' in html
    assert '<option value="Food" selected>' in html


def test_missing_description_saves_null(client, temp_db):
    login(client)
    r = client.post("/expenses/add", data=valid_form(description=""))
    assert r.status_code == 302
    assert rows_for(temp_db)[-1]["description"] is None


def test_description_at_limit_is_accepted(client, temp_db):
    login(client)
    r = client.post("/expenses/add", data=valid_form(description="x" * 200))
    assert r.status_code == 302


def test_navbar_and_profile_link_to_add_expense(client):
    login(client)
    assert 'href="/expenses/add"' in client.get("/").get_data(as_text=True)
    assert 'href="/expenses/add"' in client.get("/profile").get_data(as_text=True)
