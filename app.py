import calendar
import math
import sqlite3
from datetime import date, datetime

from flask import (Flask, abort, flash, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash

from database.db import create_user, get_db, get_user_by_email, init_db, seed_db
from database.queries import (get_category_breakdown, get_recent_transactions,
                              get_expense_by_id, get_summary_stats, get_user_by_id,
                              insert_expense, update_expense, delete_expense)

CATEGORIES = ("Food", "Transport", "Bills", "Health", "Entertainment",
              "Shopping", "Other")
DESCRIPTION_MAX = 200
MIN_AMOUNT = 0.01
MAX_AMOUNT = 10_000_000

app = Flask(__name__)
app.secret_key = "spendly-dev-secret-change-me"  # development only

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method != "POST":
        abort(405)

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    # 1. All fields non-empty
    if not name or not email or not password or not confirm_password:
        flash("All fields are required.", "error")
        return render_template("register.html"), 200

    # 2. Passwords match
    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return render_template("register.html"), 200

    # 3. Email not already registered
    try:
        create_user(name, email, password)
    except sqlite3.IntegrityError:
        flash("Email already registered.", "error")
        return render_template("register.html"), 200

    flash("Account created. Please sign in.", "success")
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method != "POST":
        abort(405)

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    user = get_user_by_email(email) if email and password else None
    if user is None or not check_password_hash(user["password_hash"], password):
        flash("Invalid email or password.", "error")
        return render_template("login.html"), 200

    session["user_id"] = int(user["id"])
    return redirect(url_for("landing"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.context_processor
def inject_nav_user():
    """Navbar name for the logged-in user, or None for guests."""
    user_id = session.get("user_id")
    if not user_id:
        return {"nav_user_name": None}
    user = get_user_by_id(user_id)
    return {"nav_user_name": user["name"] if user else None}


def _parse_iso_date(value):
    """Return a date for a well-formed YYYY-MM-DD string, else None."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _months_back(today, months):
    """Return the date `months` calendar months before today, clamped to month end."""
    total = today.year * 12 + (today.month - 1) - months
    year, month = divmod(total, 12)
    month += 1
    day = min(today.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _preset_ranges(today):
    """Return the filter presets as (key, label, date_from, date_to)."""
    return [
        ("this_month", "This Month", date(today.year, today.month, 1), today),
        ("last_3", "Last 3 Months", _months_back(today, 3), today),
        ("last_6", "Last 6 Months", _months_back(today, 6), today),
        ("all", "All Time", None, None),
    ]


@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    user = get_user_by_id(user_id)
    if user is None:
        session.clear()
        return redirect(url_for("login"))

    parts = user["name"].split()
    user["initials"] = "".join(p[0] for p in parts[:2]).upper() or "?"

    today = date.today()
    start = _parse_iso_date(request.args.get("date_from"))
    end = _parse_iso_date(request.args.get("date_to"))
    if start is None or end is None:
        start = end = None
    elif start > end:
        flash("Start date must be before end date.", "error")
        start = end = None

    date_from = start.isoformat() if start else None
    date_to = end.isoformat() if end else None

    presets = []
    active_key = None
    for key, label, p_from, p_to in _preset_ranges(today):
        p_from_s = p_from.isoformat() if p_from else None
        p_to_s = p_to.isoformat() if p_to else None
        is_active = (p_from_s, p_to_s) == (date_from, date_to)
        if is_active:
            active_key = key
        params = {}
        if p_from_s and p_to_s:
            params = {"date_from": p_from_s, "date_to": p_to_s}
        presets.append({
            "label": label,
            "url": url_for("profile", **params),
            "active": is_active,
        })

    custom_active = date_from is not None and active_key is None
    if date_from is None and active_key is None:
        # no filter means the "All Time" preset is the one in effect
        presets[-1]["active"] = True

    stats = get_summary_stats(user_id, date_from, date_to)
    stats["total_spent"] = f"{stats['total_spent']:,.2f}"

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=get_recent_transactions(user_id, date_from=date_from, date_to=date_to),
        categories=get_category_breakdown(user_id, date_from, date_to),
        presets=presets,
        date_from=date_from or "",
        date_to=date_to or "",
        custom_active=custom_active,
    )


def _validate_expense_form(form):
    """Validate the add/edit expense form.

    Returns (values, cleaned, error). `values` are the stripped submitted
    strings (for re-populating the form). `cleaned` is a dict ready to save,
    or None when `error` is set.
    """
    values = {
        "amount": form.get("amount", "").strip(),
        "category": form.get("category", "").strip(),
        "date": form.get("date", "").strip(),
        "description": form.get("description", "").strip(),
    }

    # 1. amount
    amount_error = (f"Amount must be a number between {MIN_AMOUNT:.2f} "
                    f"and {MAX_AMOUNT:,}.")
    try:
        amount = float(values["amount"])
    except ValueError:
        return values, None, amount_error
    if not math.isfinite(amount) or not MIN_AMOUNT <= amount <= MAX_AMOUNT:
        return values, None, amount_error

    # 2. category
    if values["category"] not in CATEGORIES:
        return values, None, "Please choose a valid category."

    # 3. date (stored in normalized YYYY-MM-DD form)
    try:
        parsed_date = datetime.strptime(values["date"], "%Y-%m-%d").date()
    except ValueError:
        return values, None, "Please enter a valid date."

    # 4. description
    if len(values["description"]) > DESCRIPTION_MAX:
        return values, None, (
            f"Description must be {DESCRIPTION_MAX} characters or fewer.")

    return values, {
        "amount": round(amount, 2),
        "category": values["category"],
        "date": parsed_date.isoformat(),
        "description": values["description"] or None,
    }, None


@app.route("/expenses/add", methods=["GET", "POST"])
def add_expense():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template(
            "add_expense.html",
            categories=CATEGORIES,
            values={"date": date.today().isoformat()},
        )
    if request.method != "POST":
        abort(405)

    values, cleaned, error = _validate_expense_form(request.form)
    if error:
        flash(error, "error")
        return render_template("add_expense.html", categories=CATEGORIES,
                               values=values), 200

    insert_expense(session["user_id"], cleaned["amount"], cleaned["category"],
                   cleaned["date"], cleaned["description"])
    return redirect(url_for("profile"))


@app.route("/expenses/<int:id>/edit", methods=["GET", "POST"])
def edit_expense(id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    expense = get_expense_by_id(id, user_id)
    if expense is None:
        abort(404)

    if request.method == "GET":
        values = {
            "amount": f"{expense['amount']:.2f}",
            "category": expense["category"],
            "date": expense["date"],
            "description": expense["description"] or "",
        }
        return render_template("edit_expense.html", categories=CATEGORIES,
                               values=values, expense_id=id)
    if request.method != "POST":
        abort(405)

    values, cleaned, error = _validate_expense_form(request.form)
    if error:
        flash(error, "error")
        return render_template("edit_expense.html", categories=CATEGORIES,
                               values=values, expense_id=id), 200

    changed = update_expense(id, user_id, cleaned["amount"], cleaned["category"],
                             cleaned["date"], cleaned["description"])
    if changed == 0:
        abort(404)
    return redirect(url_for("profile"))


@app.route("/expenses/<int:id>/delete", methods=["POST"])
def delete_expense_route(id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    if get_expense_by_id(id, user_id) is None:
        abort(404)
    if delete_expense(id, user_id) == 0:
        abort(404)
    return redirect(url_for("profile"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
