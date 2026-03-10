# import sqlite3

# def get_connection():
#     conn = sqlite3.connect("library.db")
#     conn.row_factory = sqlite3.Row
#     return conn

import sqlite3

DB_NAME = "library.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    # BOOKS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        author TEXT,
        publisher TEXT,
        category TEXT,
        copies INTEGER
    )
    """)

    # BORROWS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS borrows (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        book_id INTEGER,
        borrow_date TEXT,
        return_date TEXT,
        status TEXT,
        fine INTEGER DEFAULT 0
    )
    """)

    # PAYMENTS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount INTEGER,
        status TEXT,
        method TEXT,
        transaction_id TEXT,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()