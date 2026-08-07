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
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number INTEGER,
        telegram_id INTEGER,
        username TEXT,
        items TEXT,
        subtotal REAL,
        shipping REAL,
        total REAL,
        delivery TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            product_id TEXT,
            quantity INTEGER
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

def get_product_sale(product_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            product_id,
            name,
            cost,
            price,
            stock
        FROM products
        WHERE product_id = ?
    """, (product_id,))

    row = cursor.fetchone()

    conn.close()

    return row

def get_product_details(product_id):
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

def add_to_cart(
    telegram_id,
    product_id,
    quantity,
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT stock
        FROM products
        WHERE product_id=?
    """, (product_id,))

    stock = cursor.fetchone()[0]

    cursor.execute("""
        SELECT quantity
        FROM cart
        WHERE telegram_id=? AND product_id=?
    """, (
        telegram_id,
        product_id,
    ))

    row = cursor.fetchone()

    current = row[0] if row else 0

    if current + quantity > stock:
        conn.close()
        return False

    if row:
        cursor.execute("""
            UPDATE cart
            SET quantity = quantity + ?
            WHERE telegram_id=? AND product_id=?
        """, (
            quantity,
            telegram_id,
            product_id,
        ))
    else:
        cursor.execute("""
            INSERT INTO cart
            (
                telegram_id,
                product_id,
                quantity
            )
            VALUES (?, ?, ?)
        """, (
            telegram_id,
            product_id,
            quantity,
        ))

    conn.commit()
    conn.close()

    return True

def get_cart(telegram_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            cart.product_id,
            products.name,
            products.price,
            cart.quantity
        FROM cart
        JOIN products
        ON cart.product_id = products.product_id
        WHERE telegram_id=?
    """, (telegram_id,))

    rows = cursor.fetchall()

    conn.close()

    return rows

def get_cart_quantity(telegram_id, product_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT quantity
        FROM cart
        WHERE telegram_id=? AND product_id=?
    """, (
        telegram_id,
        product_id,
    ))

    row = cursor.fetchone()

    conn.close()

    if row:
        return row[0]

    return 0

def clear_cart(telegram_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM cart
        WHERE telegram_id=?
    """, (telegram_id,))

    conn.commit()
    conn.close()

def create_order(
    telegram_id,
    username,
    items,
    subtotal,
    shipping,
    total,
    delivery,
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT MAX(order_number)
        FROM orders
    """)

    row = cursor.fetchone()

    if row[0] is None:
        order_number = 1001
    else:
        order_number = row[0] + 1

    cursor.execute("""
        INSERT INTO orders
        (
            order_number,
            telegram_id,
            username,
            items,
            subtotal,
            shipping,
            total,
            delivery,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        order_number,
        telegram_id,
        username,
        items,
        subtotal,
        shipping,
        total,
        delivery,
        "Pending Verification",
    ))

    conn.commit()
    conn.close()

    return order_number

def approve_order(order_number):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE orders
        SET status='Approved'
        WHERE order_number=?
    """, (order_number,))

    conn.commit()
    conn.close()


def reject_order(order_number):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE orders
        SET status='Rejected'
        WHERE order_number=?
    """, (order_number,))

    conn.commit()
    conn.close()
    
def get_order(order_number):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            telegram_id,
            username,
            items,
            subtotal,
            shipping,
            total,
            delivery,
            status
        FROM orders
        WHERE order_number=?
    """, (order_number,))

    row = cursor.fetchone()

    conn.close()

    return row

init_db()
