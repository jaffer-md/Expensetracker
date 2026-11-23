import sqlite3

import database.db as dbm
from database.queries import delete_expense


def login(client, email="demo@spendly.com", password="demo123"):
    client.post("/login", data=dict(email=email, password=password))


def other_user_login(client):
    dbm.create_user("Other Person", "other@spendly.com", "secret123")
    login(client, "other@spendly.com", "secret123")


def exists(temp_db, expense_id):
    conn = sqlite3.connect(str(temp_db))
    r = conn.execute("SELECT 1 FROM expenses WHERE id = ?", (expense_id,)).fetchone()
    conn.close()
    return r is not None


def count(temp_db):
    conn = sqlite3.connect(str(temp_db))
    n = conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
    conn.close()
    return n


# ------------------------------ queries -------------------------------- #

def test_delete_expense_owner_removes_row(temp_db):
    assert delete_expense(1, 1) == 1
    assert not exists(temp_db, 1)


def test_delete_expense_wrong_user_keeps_row(temp_db):
    assert delete_expense(1, 2) == 0
    assert exists(temp_db, 1)


def test_delete_expense_missing_id_is_noop(temp_db):
    before = count(temp_db)
    assert delete_expense(9999, 1) == 0
    assert count(temp_db) == before


# ------------------------------- routes -------------------------------- #

def test_post_requires_login(client, temp_db):
    r = client.post("/expenses/1/delete")
    assert r.status_code == 302 and r.headers["Location"].endswith("/login")
    assert exists(temp_db, 1)


def test_post_own_expense_deletes_and_redirects(client, temp_db):
    login(client)
    before = count(temp_db)
    r = client.post("/expenses/1/delete")
    assert r.status_code == 302 and r.headers["Location"].endswith("/profile")
    assert not exists(temp_db, 1)
    assert count(temp_db) == before - 1


def test_post_other_users_expense_is_404_and_kept(client, temp_db):
    other_user_login(client)
    assert client.post("/expenses/1/delete").status_code == 404
    assert exists(temp_db, 1)


def test_post_missing_expense_is_404(client):
    login(client)
    assert client.post("/expenses/9999/delete").status_code == 404


def test_get_is_405(client, temp_db):
    login(client)
    assert client.get("/expenses/1/delete").status_code == 405
    assert exists(temp_db, 1)


def test_deleted_expense_disappears_from_profile(client):
    login(client)
    client.post("/expenses/1/delete")
    html = client.get("/profile").get_data(as_text=True)
    assert "/expenses/1/edit" not in html
    assert "/expenses/1/delete" not in html


def test_profile_rows_have_edit_and_delete(client):
    login(client)
    html = client.get("/profile").get_data(as_text=True)
    for expense_id in range(1, 9):
        assert f'action="/expenses/{expense_id}/delete"' in html
        assert f'href="/expenses/{expense_id}/edit"' in html
    assert 'class="btn-delete"' in html
    assert "onsubmit=\"return confirm('Delete this expense?')\"" in html
    assert 'style="display:inline"' in html
