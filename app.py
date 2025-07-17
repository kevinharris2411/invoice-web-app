from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect('invoice.db')
    cursor = conn.cursor()

    # Create customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT,
            address TEXT
        )
    ''')

    # Create invoices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            date TEXT,
            total_amount REAL,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )
    ''')

    # Create items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            item_name TEXT,
            qty INTEGER,
            price REAL,
            total REAL,
            FOREIGN KEY(invoice_id) REFERENCES invoices(id)
        )
    ''')

    conn.commit()
    conn.close()


# ---------- ROUTES ----------
@app.route('/')
def home():
    # Redirect straight to create page for user ease
    return redirect('/create')

@app.route('/create', methods=['GET'])
def create_invoice():
    return render_template('create_invoice.html')


@app.route('/submit', methods=['POST'])
def submit_invoice():
    # Collect customer info
    name = request.form['name']
    contact = request.form['contact']
    address = request.form['address']

    # Collect item list
    item_names = request.form.getlist('item_name[]')
    qtys = request.form.getlist('qty[]')
    prices = request.form.getlist('price[]')

    items = []
    total_amount = 0

    # Calculate total and organize item entries
    for name_i, qty_i, price_i in zip(item_names, qtys, prices):
        qty_i = int(qty_i)
        price_i = float(price_i)
        total = qty_i * price_i
        items.append({
            'item_name': name_i,
            'qty': qty_i,
            'price': price_i,
            'total': total
        })
        total_amount += total

    # Store into database
    conn = sqlite3.connect('invoice.db')
    cursor = conn.cursor()

    # Insert customer
    cursor.execute("INSERT INTO customers (name, contact, address) VALUES (?, ?, ?)", (name, contact, address))
    customer_id = cursor.lastrowid

    # Insert invoice
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO invoices (customer_id, date, total_amount) VALUES (?, ?, ?)",
                   (customer_id, date, total_amount))
    invoice_id = cursor.lastrowid

    # Insert each item
    for item in items:
        cursor.execute(
            "INSERT INTO items (invoice_id, item_name, qty, price, total) VALUES (?, ?, ?, ?, ?)",
            (invoice_id, item['item_name'], item['qty'], item['price'], item['total'])
        )

    conn.commit()
    conn.close()

    # Show invoice summary page
    return render_template(
        'invoice_summary.html',
        name=name,
        contact=contact,
        address=address,
        date=date,
        items=items,
        total_amount=total_amount
    )


# ---------- MAIN ----------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
