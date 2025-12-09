import sqlite3

DB_NAME = "data.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # user table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0,
            referred_by INTEGER NULL
        );
    """)

    # referral tracking
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

    c.execute("INSERT INTO referrals (referrer_id, referred_id) VALUES (?, ?)", (referrer, referred))

    conn.commit()
    conn.close()


def complete_referral(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # mark referral done
    c.execute("UPDATE referrals SET completed=1 WHERE referred_id=?", (user_id,))

    # give balance
    c.execute("""
        UPDATE users 
        SET balance = balance + 10
        WHERE user_id = (SELECT referrer_id FROM referrals WHERE referred_id=?)
    """, (user_id,))

    conn.commit()
    conn.close()


def get_balance(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()

    conn.close()

    return result[0] if result else 0
