import sqlite3

DB_NAME = "tickets.db"

def all_tickets():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT ticket_number, full_name, username, claimed_at
        FROM tickets
        ORDER BY ticket_number
    """)

    rows = cur.fetchall()
    conn.close()

    return rows

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            full_name TEXT,
            username TEXT,
            ticket_number INTEGER UNIQUE,
            claimed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO settings (key, value)
        VALUES ('giveaway_open', '0')
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT UNIQUE,
            name TEXT,
            category TEXT,
            product_type TEXT,
            cost REAL,
            price REAL,
            stock INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT,
            product_name TEXT,
            quantity INTEGER,
            cost REAL,
            selling REAL,
            total REAL,
            profit REAL,
            customer TEXT,
            payment TEXT,
            sold_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)    
    
    conn.commit()
    conn.close()


def is_giveaway_open():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT value FROM settings WHERE key='giveaway_open'"
    )

    result = cursor.fetchone()

    conn.close()

    return result[0] == "1"


def open_giveaway():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE settings
        SET value='1'
        WHERE key='giveaway_open'
    """)

    conn.commit()
    conn.close()


def close_giveaway():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE settings
        SET value='0'
        WHERE key='giveaway_open'
    """)

    conn.commit()
    conn.close()


def has_ticket(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ticket_number
        FROM tickets
        WHERE telegram_id=?
    """, (user_id,))

    result = cursor.fetchone()

    conn.close()

    return result


def get_next_ticket():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT MAX(ticket_number)
        FROM tickets
    """)

    result = cursor.fetchone()[0]

    conn.close()

    if result is None:
        return 1

    return result + 1


def create_ticket(user):
    ticket = get_next_ticket()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tickets
        (
            telegram_id,
            full_name,
            username,
            ticket_number
        )
        VALUES
        (
            ?, ?, ?, ?
        )
    """, (
        user.id,
        user.full_name,
        user.username,
        ticket
    ))

    conn.commit()
    conn.close()

    return ticket


def ticket_count():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM tickets
    """)

    count = cursor.fetchone()[0]

    conn.close()

    return count
    
# ==========================
# PRODUCTS
# ==========================

def add_product(product_id, name, category, product_type, cost, price, stock):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO products
        (
            product_id,
            name,
            category,
            product_type,
            cost,
            price,
            stock
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        product_id,
        name,
        category,
        product_type,
        cost,
        price,
        stock
    ))

    conn.commit()
    conn.close()


def get_products():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            product_id,
            name,
            category,
            product_type,
            cost,
            price,
            stock
        FROM products
        WHERE active = 1
        ORDER BY category, name
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows

def add_stock(product_id, quantity):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET stock = stock + ?
        WHERE product_id = ?
    """, (
        quantity,
        product_id
    ))

    conn.commit()
    conn.close()

def remove_stock(product_id, quantity):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET stock = stock - ?
        WHERE product_id = ?
    """, (
        quantity,
        product_id
    ))

    conn.commit()
    conn.close()

def get_product(product_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            product_id,
            name,
            stock
        FROM products
        WHERE product_id=?
    """, (product_id,))

    row = cursor.fetchone()

    conn.close()

    return row

def record_sale(
    product_id,
    product_name,
    quantity,
    cost,
    selling,
    customer,
    payment,
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    total = selling * quantity
    profit = (selling - cost) * quantity

    cursor.execute("""
        INSERT INTO sales
        (
            product_id,
            product_name,
            quantity,
            cost,
            selling,
            total,
            profit,
            customer,
            payment
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        product_id,
        product_name,
        quantity,
        cost,
        selling,
        total,
        profit,
        customer,
        payment,
    ))

    conn.commit()
    conn.close()    
init_db()
