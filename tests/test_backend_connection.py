import sqlite3

import pytest

import database.db as dbm
from database.queries import (
    get_category_breakdown,
    get_recent_transactions,
    get_summary_stats,
    get_user_by_id,
)

SEED_TOTAL = 388.49


def login(client, email="demo@spendly.com", password="demo123"):
    return client.post("/login", data=dict(email=email, password=password))


def new_user_id(email="new@spendly.com"):
    return dbm.create_user("New User", email, "secret123")


# ---------------------------- get_user_by_id ------------------------- #

def test_get_user_by_id_returns_seed_user(temp_db):
    user = get_user_by_id(1)
    assert user["name"] == "Demo User"
    assert user["email"] == "demo@spendly.com"
    assert user["member_since"]  # "Month YYYY"
    assert len(user["member_since"].split()) == 2
    assert user["member_since"].split()[1].isdigit()


def test_get_user_by_id_missing_returns_none(temp_db):
    assert get_user_by_id(9999) is None


# --------------------------- get_summary_stats ----------------------- #

def test_summary_stats_with_expenses(temp_db):
    stats = get_summary_stats(1)
    assert stats["total_spent"] == pytest.approx(SEED_TOTAL)
    assert stats["transaction_count"] == 8
    assert stats["top_category"] == "Bills"


def test_summary_stats_no_expenses(temp_db):
    uid = new_user_id()
    assert get_summary_stats(uid) == {
        "total_spent": 0,
        "transaction_count": 0,
        "top_category": "—",
    }


# ------------------------ get_recent_transactions -------------------- #

def test_recent_transactions_newest_first(temp_db):
    rows = get_recent_transactions(1)
    assert len(rows) == 8
    dates = [r["date"] for r in rows]
    assert dates == sorted(dates, reverse=True)
    assert set(rows[0].keys()) == {"id", "date", "description", "category", "amount"}


def test_recent_transactions_limit(temp_db):
    assert len(get_recent_transactions(1, limit=3)) == 3


def test_recent_transactions_no_expenses(temp_db):
    assert get_recent_transactions(new_user_id()) == []


# ------------------------ get_category_breakdown --------------------- #

def test_category_breakdown_order_and_pct(temp_db):
    cats = get_category_breakdown(1)
    assert len(cats) == 7
    amounts = [c["amount"] for c in cats]
    assert amounts == sorted(amounts, reverse=True)
    assert all(isinstance(c["pct"], int) for c in cats)
    assert sum(c["pct"] for c in cats) == 100
    assert {c["name"] for c in cats} == {
        "Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other",
    }


def test_category_breakdown_no_expenses(temp_db):
    assert get_category_breakdown(new_user_id()) == []


def test_category_pct_remainder_goes_to_largest(temp_db):
    # Three equal categories: 33 + 33 + 33 = 99, so the largest absorbs 1.
    conn = sqlite3.connect(str(temp_db))
    conn.execute("DELETE FROM expenses")
    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date) VALUES (1, 10, ?, '2026-11-01')",
        [("Food",), ("Bills",), ("Health",)],
    )
    conn.commit()
    conn.close()
    cats = get_category_breakdown(1)
    assert sum(c["pct"] for c in cats) == 100
    assert cats[0]["pct"] == 34


# ------------------------------- routes ------------------------------ #

def test_profile_requires_login(client):
    r = client.get("/profile")
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/login")


def test_profile_shows_seed_user_data(client):
    login(client)
    r = client.get("/profile")
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert "Demo User" in html
    assert "demo@spendly.com" in html
    assert "₹" in html
    assert "388.49" in html
    assert ">8<" in html  # transaction count tile
    assert "Bills" in html
    # newest-first: 2026-11-19 row appears before 2026-11-01
    table = html[html.index("txn-table"):]
    assert table.index("2026-11-19") < table.index("2026-11-01")
    for name in ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]:
        assert f'badge-{name.lower()}' in html


def test_profile_new_user_empty_state(client):
    new_user_id()
    login(client, "new@spendly.com", "secret123")
    r = client.get("/profile")
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert "₹0.00" in html
    assert "New User" in html
    assert "category-row" not in html


def test_navbar_shows_db_user_name(client):
    login(client)
    html = client.get("/").get_data(as_text=True)
    assert "Demo User" in html
    assert "Sign out" in html
