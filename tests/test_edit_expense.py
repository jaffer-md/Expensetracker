import sqlite3

import database.db as dbm
from database.queries import get_expense_by_id, update_expense


def login(client, email="demo@spendly.com", password="demo123"):
    client.post("/login", data=dict(email=email, password=password))


def other_user_login(client):
    dbm.create_user("Other Person", "other@spendly.com", "secret123")
    login(client, "other@spendly.com", "secret123")


def valid_form(**overrides):
    data = dict(amount="99.0", category="Bills", date="2026-03-20", description="Updated")
    data.update(overrides)
    return data


def row(temp_db, expense_id):
    conn = sqlite3.connect(str(temp_db))
    conn.row_factory = sqlite3.Row
    r = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
    conn.close()
    return dict(r) if r else None


# ------------------------------ queries -------------------------------- #

def test_get_expense_by_id_owner(temp_db):
    e = get_expense_by_id(1, 1)
    assert e["id"] == 1 and e["description"] == "Lunch" and e["category"] == "Food"


def test_get_expense_by_id_wrong_user(temp_db):
    assert get_expense_by_id(1, 2) is None


def test_get_expense_by_id_missing(temp_db):
    assert get_expense_by_id(9999, 1) is None


def test_update_expense_owner(temp_db):
    assert update_expense(1, 1, 99.0, "Bills", "2026-03-20", "Updated") == 1
    r = row(temp_db, 1)
    assert r["amount"] == 99.0 and r["category"] == "Bills"
    assert r["date"] == "2026-03-20" and r["description"] == "Updated"


def test_update_expense_wrong_user_changes_nothing(temp_db):
    before = row(temp_db, 1)
    assert update_expense(1, 2, 99.0, "Bills", "2026-03-20", "Hacked") == 0
    assert row(temp_db, 1) == before


# ------------------------------- routes -------------------------------- #

def test_get_requires_login(client):
    r = client.get("/expenses/1/edit")
    assert r.status_code == 302 and r.headers["Location"].endswith("/login")


def test_post_requires_login(client, temp_db):
    before = row(temp_db, 1)
    r = client.post("/expenses/1/edit", data=valid_form())
    assert r.status_code == 302 and r.headers["Location"].endswith("/login")
    assert row(temp_db, 1) == before


def test_get_prefilled_form(client):
    login(client)
    r = client.get("/expenses/1/edit")
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert 'value="12.50"' in html
    assert 'value="2026-11-01"' in html
    assert 'value="Lunch"' in html
    assert '<option value="Food" selected>' in html
    assert html.count("<option ") == 7
    assert 'action="/expenses/1/edit"' in html
    assert "Save Changes" in html


def test_get_other_users_expense_is_404(client):
    other_user_login(client)
    assert client.get("/expenses/1/edit").status_code == 404


def test_get_missing_expense_is_404(client):
    login(client)
    assert client.get("/expenses/9999/edit").status_code == 404


def test_post_other_users_expense_is_404_and_unchanged(client, temp_db):
    before = row(temp_db, 1)
    other_user_login(client)
    assert client.post("/expenses/1/edit", data=valid_form()).status_code == 404
    assert row(temp_db, 1) == before


def test_valid_post_updates_and_redirects(client, temp_db):
    login(client)
    r = client.post("/expenses/1/edit", data=valid_form())
    assert r.status_code == 302 and r.headers["Location"].endswith("/profile")
    r = row(temp_db, 1)
    assert r["amount"] == 99.0 and r["category"] == "Bills"
    assert r["date"] == "2026-03-20" and r["description"] == "Updated"


def test_updated_values_appear_on_profile(client):
    login(client)
    client.post("/expenses/1/edit", data=valid_form(description="Edited lunch"))
    html = client.get("/profile").get_data(as_text=True)
    assert "Edited lunch" in html


def _assert_rejected(client, temp_db, **overrides):
    login(client)
    before = row(temp_db, 1)
    r = client.post("/expenses/1/edit", data=valid_form(**overrides))
    assert r.status_code == 200
    assert b"auth-error" in r.data
    assert row(temp_db, 1) == before
    return r


def test_missing_amount(client, temp_db):
    _assert_rejected(client, temp_db, amount="")


def test_zero_amount(client, temp_db):
    _assert_rejected(client, temp_db, amount="0")


def test_non_numeric_amount(client, temp_db):
    _assert_rejected(client, temp_db, amount="abc")


def test_invalid_category(client, temp_db):
    _assert_rejected(client, temp_db, category="Gadgets")


def test_invalid_date(client, temp_db):
    _assert_rejected(client, temp_db, date="not-a-date")


def test_rejection_keeps_submitted_not_original_values(client, temp_db):
    r = _assert_rejected(client, temp_db, amount="0", description="Typed this")
    html = r.get_data(as_text=True)
    assert "Typed this" in html
    assert 'value="Lunch"' not in html
    assert 'value="2026-03-20"' in html
    assert '<option value="Bills" selected>' in html


def test_blank_description_saves_null(client, temp_db):
    login(client)
    r = client.post("/expenses/1/edit", data=valid_form(description=""))
    assert r.status_code == 302
    assert row(temp_db, 1)["description"] is None


# --------------- hardening shared with Add Expense (Step 7) ------------ #

def test_huge_amount_rejected_and_profile_still_renders(client, temp_db):
    _assert_rejected(client, temp_db, amount="1e308")
    assert client.get("/profile").status_code == 200


def test_sub_paisa_amount_rejected(client, temp_db):
    _assert_rejected(client, temp_db, amount="0.001")


def test_amount_rounded_to_two_decimals(client, temp_db):
    login(client)
    client.post("/expenses/1/edit", data=valid_form(amount="50.129"))
    assert row(temp_db, 1)["amount"] == 50.13


def test_date_is_normalized_on_save(client, temp_db):
    login(client)
    client.post("/expenses/1/edit", data=valid_form(date="2026-3-5"))
    assert row(temp_db, 1)["date"] == "2026-03-05"


def test_add_expense_gets_same_hardening(client, temp_db):
    login(client)
    r = client.post("/expenses/add", data=valid_form(amount="1e308"))
    assert r.status_code == 200
    client.post("/expenses/add", data=valid_form(amount="12.345", date="2026-3-5"))
    conn = sqlite3.connect(str(temp_db))
    amount, d = conn.execute(
        "SELECT amount, date FROM expenses ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    assert amount == 12.35 and d == "2026-03-05"


# ------------------------------ profile -------------------------------- #

def test_profile_has_actions_column_and_edit_links(client):
    login(client)
    html = client.get("/profile").get_data(as_text=True)
    assert "<th>Actions</th>" in html
    for expense_id in range(1, 9):
        assert f'href="/expenses/{expense_id}/edit"' in html
