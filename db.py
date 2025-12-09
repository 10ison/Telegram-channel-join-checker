import sqlite3, time

DB = "data.db"

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0,
            referred_by INTEGER,
            verified INTEGER DEFAULT 0,
            created_at INTEGER
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS withdrawals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            upi TEXT,
            status TEXT,
            created_at INTEGER
        )
    """)
    conn.commit()
    conn.close()

def get_user(telegram_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT balance, referred_by, verified FROM users WHERE telegram_id=?", (telegram_id,))
    row = cur.fetchone()
    conn.close()
    return row

def create_user(telegram_id, referred_by=None):
    conn = sqlite3.connect(DB)
    conn.execute(
        "INSERT OR IGNORE INTO users (telegram_id, referred_by, created_at) VALUES (?,?,?)",
        (telegram_id, referred_by, int(time.time()))
    )
    conn.commit()
    conn.close()

def mark_verified(telegram_id):
    conn = sqlite3.connect(DB)
    conn.execute("UPDATE users SET verified=1 WHERE telegram_id=?", (telegram_id,))
    conn.commit()
    conn.close()

def credit_referral(referrer_id):
    conn = sqlite3.connect(DB)
    conn.execute("UPDATE users SET balance = balance + 10 WHERE telegram_id=?", (referrer_id,))
    conn.commit()
    conn.close()

def get_balance(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE telegram_id=?", (user_id,))
    b = c.fetchone()
    conn.close()
    return b[0] if b else 0

def create_withdraw(user_id, amount, upi):
    conn = sqlite3.connect(DB)
    conn.execute(
        "INSERT INTO withdrawals (user_id, amount, upi, status, created_at) VALUES (?,?,?,'Pending',?)",
        (user_id, amount, upi, int(time.time()))
    )
    conn.commit()
    conn.close()

def list_pending_withdrawals():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id, user_id, amount, upi FROM withdrawals WHERE status='Pending'")
    rows = cur.fetchall()
    conn.close()
    return rows

def approve_withdraw(id):
    conn = sqlite3.connect(DB)
    conn.execute("UPDATE withdrawals SET status='Approved' WHERE id=?", (id,))
    conn.commit()
    conn.close()

def reject_withdraw(id):
    conn = sqlite3.connect(DB)
    conn.execute("UPDATE withdrawals SET status='Rejected' WHERE id=?", (id,))
    conn.commit()
    conn.close()
