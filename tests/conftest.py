import os
import sys

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import database.db as dbm  # noqa: E402


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """Point the app at a fresh, seeded temp database (never spendly.db)."""
    db_file = tmp_path / "test.db"
    monkeypatch.setattr(dbm, "DB_PATH", str(db_file))
    dbm.init_db()
    dbm.seed_db()
    # seed_db() clamps dates to today's day-of-month, so pin them to fixed
    # values to keep tests independent of the date they run on.
    fixed_dates = {1: "2026-11-01", 2: "2026-11-03", 3: "2026-11-05",
                   4: "2026-11-07", 5: "2026-11-10", 6: "2026-11-14",
                   7: "2026-11-18", 8: "2026-11-19"}
    conn = dbm.get_db()
    try:
        conn.executemany("UPDATE expenses SET date = ? WHERE id = ?",
                         [(d, i) for i, d in fixed_dates.items()])
        conn.commit()
    finally:
        conn.close()
    return db_file


@pytest.fixture
def client(temp_db):
    from app import app

    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture
def seed_user_id(temp_db):
    return 1
