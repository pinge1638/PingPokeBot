import sqlite3

DB_NAME = "tickets.db"

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


def all_tickets():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ticket_number,
            full_name,
            username
        FROM tickets
        ORDER BY ticket_number
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows
