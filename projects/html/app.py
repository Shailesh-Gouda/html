from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ---------- MENU ITEMS ----------
MENU_PRICES = {
    "Fried Rice": 120,
    "Noodles": 100,
    "Manchurian": 150,
    "Paneer Butter Masala": 180
}

# ---------- DATABASE ----------
def get_db():
    return sqlite3.connect("database.db")


def init_db():
    db = get_db()

    db.execute("""
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_id INTEGER,
        items TEXT,
        status TEXT,
        prep_time TEXT,
        total INTEGER
    )
    """)

    db.commit()


init_db()


@app.route("/")
def home():
    return render_template("home.html")


# ---------- CUSTOMER MENU ----------
@app.route("/menu/<int:table_id>")
def menu(table_id):
    return render_template(
        "menu.html",
        table_id=table_id,
        menu=MENU_PRICES
    )


# ---------- PLACE ORDER ----------
@app.route("/place_order", methods=["POST"])
def place_order():

    table_id = request.form["table_id"]

    order_items = []
    total = 0

    for item, price in MENU_PRICES.items():

        qty = request.form.get(item)

        if qty and qty.isdigit() and int(qty) > 0:
            qty = int(qty)
            item_total = qty * price
            total += item_total
            order_items.append(f"{item} x {qty} = ₹{item_total}")

    if not order_items:
        return "Select at least one item"

    items_text = " | ".join(order_items)

    db = get_db()

    db.execute(
        "INSERT INTO orders(table_id,items,status,prep_time,total) VALUES(?,?,?,?,?)",
        (table_id, items_text, "Pending", "-", total)
    )

    db.commit()

    return redirect("/success")


# ---------- KITCHEN PANEL ----------
@app.route("/kitchen")
def kitchen():

    db = get_db()

    orders = db.execute(
        "SELECT * FROM orders WHERE status='Pending'"
    ).fetchall()

    return render_template("kitchen.html", orders=orders)


@app.route("/accept/<int:order_id>")
def accept(order_id):

    db = get_db()

    db.execute(
        "UPDATE orders SET status='Preparing', prep_time='15 Minutes' WHERE id=?",
        (order_id,)
    )

    db.commit()

    return redirect("/kitchen")


# ---------- BILLING PANEL ----------
@app.route("/billing")
def billing():

    db = get_db()

    orders = db.execute(
        "SELECT * FROM orders WHERE status='Preparing'"
    ).fetchall()

    return render_template("billing.html", orders=orders)


@app.route("/paid/<int:order_id>")
def paid(order_id):

    db = get_db()

    db.execute(
        "UPDATE orders SET status='Paid' WHERE id=?",
        (order_id,)
    )

    db.commit()

    return redirect("/billing")


# ---------- SUCCESS PAGE ----------
@app.route("/success")
def success():
    return render_template("success.html")


if __name__ == "__main__":
    app.run(debug=True)
