from datetime import datetime

from database.db import get_db


def get_user_by_id(user_id):
    """Return {name, email, member_since} for the user, or None if missing."""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT name, email, created_at FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    created = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S")
    return {
        "name": row["name"],
        "email": row["email"],
        "member_since": created.strftime("%B %Y"),
    }


def _date_clause(date_from, date_to):
    """Return (sql_fragment, params) for an optional inclusive date range.

    Both bounds must be given to filter; otherwise there is no date clause.
    """
    if date_from and date_to:
        return " AND date BETWEEN ? AND ?", (date_from, date_to)
    return "", ()


def get_summary_stats(user_id, date_from=None, date_to=None):
    """Return total_spent, transaction_count and top_category for the user."""
    clause, params = _date_clause(date_from, date_to)
    conn = get_db()
    try:
        totals = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total, COUNT(*) AS count "
            "FROM expenses WHERE user_id = ?" + clause,
            (user_id, *params),
        ).fetchone()

        top = conn.execute(
            "SELECT category FROM expenses WHERE user_id = ?" + clause +
            " GROUP BY category ORDER BY SUM(amount) DESC, category ASC LIMIT 1",
            (user_id, *params),
        ).fetchone()
    finally:
        conn.close()

    return {
        "total_spent": round(totals["total"], 2),
        "transaction_count": totals["count"],
        "top_category": top["category"] if top else "—",
    }


def get_recent_transactions(user_id, limit=10, date_from=None, date_to=None):
    """Return up to `limit` expenses for the user, newest first."""
    clause, params = _date_clause(date_from, date_to)
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT id, date, description, category, amount FROM expenses "
            "WHERE user_id = ?" + clause + " ORDER BY date DESC, id DESC LIMIT ?",
            (user_id, *params, limit),
        ).fetchall()
    finally:
        conn.close()

    return [dict(row) for row in rows]


def get_category_breakdown(user_id, date_from=None, date_to=None):
    """Return per-category totals ordered by amount desc, with integer pct.

    pct values sum to exactly 100; any rounding remainder goes to the
    largest category.
    """
    clause, params = _date_clause(date_from, date_to)
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT category AS name, SUM(amount) AS amount FROM expenses "
            "WHERE user_id = ?" + clause + " GROUP BY category "
            "ORDER BY amount DESC, name ASC",
            (user_id, *params),
        ).fetchall()
    finally:
        conn.close()

    if not rows:
        return []

    grand_total = sum(row["amount"] for row in rows)
    if grand_total <= 0:
        return [
            {"name": row["name"], "amount": round(row["amount"], 2), "pct": 0}
            for row in rows
        ]

    categories = [
        {
            "name": row["name"],
            "amount": round(row["amount"], 2),
            "pct": round(row["amount"] * 100 / grand_total),
        }
        for row in rows
    ]

    remainder = 100 - sum(c["pct"] for c in categories)
    categories[0]["pct"] += remainder
    return categories


def insert_expense(user_id, amount, category, date, description):
    """Insert an expense row and return its id. description may be None."""
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO expenses (user_id, amount, category, date, description) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, amount, category, date, description),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_expense_by_id(expense_id, user_id):
    """Return the expense as a dict if it belongs to user_id, else None."""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT id, user_id, amount, category, date, description "
            "FROM expenses WHERE id = ? AND user_id = ?",
            (expense_id, user_id),
        ).fetchone()
    finally:
        conn.close()
    return dict(row) if row else None


def update_expense(expense_id, user_id, amount, category, date, description):
    """Update an expense owned by user_id. Returns the number of rows changed."""
    conn = get_db()
    try:
        cur = conn.execute(
            "UPDATE expenses SET amount = ?, category = ?, date = ?, description = ? "
            "WHERE id = ? AND user_id = ?",
            (amount, category, date, description, expense_id, user_id),
        )
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()


def delete_expense(expense_id, user_id):
    """Delete an expense owned by user_id. Returns the number of rows removed."""
    conn = get_db()
    try:
        cur = conn.execute(
            "DELETE FROM expenses WHERE id = ? AND user_id = ?",
            (expense_id, user_id),
        )
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()
