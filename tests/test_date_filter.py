import pytest

import database.db as dbm
from app import _months_back
from datetime import date
from database.queries import (
    get_category_breakdown,
    get_recent_transactions,
    get_summary_stats,
)


def login(client):
    client.post("/login", data=dict(email="demo@spendly.com", password="demo123"))


def table_html(html):
    return html[html.index("txn-table"):]


# ------------------------------ helpers -------------------------------- #

def test_months_back_clamps_to_month_end():
    assert _months_back(date(2026, 3, 31), 1) == date(2026, 2, 28)
    assert _months_back(date(2026, 11, 19), 3) == date(2026, 8, 19)
    assert _months_back(date(2026, 1, 15), 6) == date(2025, 7, 15)


# ------------------------------ queries -------------------------------- #

def test_queries_filtered_range(temp_db):
    stats = get_summary_stats(1, "2026-11-05", "2026-11-10")
    assert stats["transaction_count"] == 3
    assert stats["total_spent"] == pytest.approx(20 + 120 + 60)
    assert stats["top_category"] == "Bills"

    rows = get_recent_transactions(1, date_from="2026-11-05", date_to="2026-11-10")
    assert [r["date"] for r in rows] == ["2026-11-10", "2026-11-07", "2026-11-05"]

    cats = get_category_breakdown(1, "2026-11-05", "2026-11-10")
    assert sum(c["pct"] for c in cats) == 100
    assert {c["name"] for c in cats} == {"Transport", "Bills", "Health"}


def test_queries_one_bound_is_ignored(temp_db):
    assert get_summary_stats(1, "2026-11-05", None)["transaction_count"] == 8


def test_queries_empty_range(temp_db):
    assert get_summary_stats(1, "2020-01-01", "2020-01-31") == {
        "total_spent": 0,
        "transaction_count": 0,
        "top_category": "—",
    }
    assert get_recent_transactions(1, date_from="2020-01-01", date_to="2020-01-31") == []
    assert get_category_breakdown(1, "2020-01-01", "2020-01-31") == []


# ------------------------------- routes -------------------------------- #

def test_no_params_is_unfiltered(client):
    login(client)
    html = client.get("/profile").get_data(as_text=True)
    assert "388.49" in html
    assert "2026-11-01" in table_html(html)


def test_custom_range(client):
    login(client)
    html = client.get("/profile?date_from=2026-11-05&date_to=2026-11-10").get_data(as_text=True)
    assert "₹200.00" in html  # 20 + 120 + 60
    t = table_html(html)
    assert "2026-11-10" in t and "2026-11-05" in t
    assert "2026-11-01" not in t and "2026-11-18" not in t


def test_reversed_range_flashes_and_falls_back(client):
    login(client)
    r = client.get("/profile?date_from=2026-11-10&date_to=2026-11-05")
    html = r.get_data(as_text=True)
    assert r.status_code == 200
    assert "Start date must be before end date." in html
    assert "388.49" in html


def test_malformed_date_falls_back(client):
    login(client)
    r = client.get("/profile?date_from=not-a-date&date_to=2026-11-10")
    assert r.status_code == 200
    assert "388.49" in r.get_data(as_text=True)


def test_empty_range_shows_zero(client):
    login(client)
    html = client.get("/profile?date_from=2020-01-01&date_to=2020-01-31").get_data(as_text=True)
    assert "₹0.00" in html
    assert "category-row" not in html


def test_all_time_preset_is_clean_url_and_active_when_unfiltered(client):
    login(client)
    html = client.get("/profile").get_data(as_text=True)
    assert 'href="/profile"' in html
    assert 'class="preset-link active"' in html
    assert html.count('preset-link active') == 1
    assert "All Time" in html


def test_preset_links_include_range_and_custom_inputs_prefilled(client):
    login(client)
    html = client.get("/profile?date_from=2026-11-05&date_to=2026-11-10").get_data(as_text=True)
    assert 'value="2026-11-05"' in html
    assert 'value="2026-11-10"' in html
    assert 'class="custom-range active"' in html
    assert "preset-link active" not in html


def test_this_month_preset_active_on_its_range(client):
    login(client)
    real_today = date.today()
    html = client.get(
        f"/profile?date_from={real_today.replace(day=1).isoformat()}&date_to={real_today.isoformat()}"
    ).get_data(as_text=True)
    assert 'class="preset-link active">This Month' in html
