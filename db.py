import sqlite3

DB_NAME = "data.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0,
            referred_by INTEGER
        );
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER,
            referred_id INTEGER,
            completed INTEGER DEFAULT 0
        );
    """)

    conn.commit()
    conn.close()


def add_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()


def set_referrer(user_id, referrer):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET referred_by=? WHERE user_id=?", (referrer, user_id))
    conn.commit()
    conn.close()


def add_referral(referrer, referred):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO referrals (referrer_id, referred_id) VALUES (?,?)", (referrer, referred))
    conn.commit()
    conn.close()


def complete_referral(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # reward referral only once
    c.execute("SELECT referrer_id FROM referrals WHERE referred_id=? AND completed=0", (user_id,))
    row = c.fetchone()

    if row:
        referrer = row[0]
        c.execute("UPDATE users SET balance = balance + 10 WHERE user_id=?", (referrer,))
        c.execute("UPDATE referrals SET completed=1 WHERE referred_id=?", (user_id,))

    conn.commit()
    conn.close()


def get_balance(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    r = c.fetchone()
    conn.close()
    return r[0] if r else 0
