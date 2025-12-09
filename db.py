import sqlite3

DB = "data.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT UNIQUE,
            balance INTEGER DEFAULT 0,
            ref TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_user(uid, ref=None):
    conn = sqlite3.connect(DB)
    try:
        conn.execute("INSERT INTO users (user_id, ref) VALUES (?,?)", (uid, ref))
    except:
        pass
    conn.commit()
    conn.close()


def add_balance(uid, amount):
    conn = sqlite3.connect(DB)
    conn.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, uid))
    conn.commit()
    conn.close()


def get_balance(uid):
    conn = sqlite3.connect(DB)
    c = conn.execute("SELECT balance FROM users WHERE user_id=?", (uid,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0
