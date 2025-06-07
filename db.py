import sqlite3
from datetime import datetime
from utils import extract_title_and_asin, is_valid_amazon_url
from urllib.parse import urlparse, urlunparse

DB_NAME = "books.db"

def update_book_price(book_id, price):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE books
        SET last_price = ?, last_check = ?
        WHERE id = ?
        """, (price, datetime.now().isoformat(), book_id))
        conn.commit()

def create_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn

def create_table():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            price REAL NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY(book_id) REFERENCES books(id)
            )
        """)
        conn.commit()
def clean_url(url):
    parsed = urlparse(url)
    return urlunparse(((parsed.scheme, parsed.netloc, parsed.path, '', '', '')))

def add_book(url, title=None, asin=None):
    url = clean_url(url)
    with create_connection() as conn:
        cursor = conn.cursor()

        # Check for duplicate URL
        cursor.execute("SELECT id FROM books WHERE url = ?", (url,))
        existing_url = cursor.fetchone()
        if not is_valid_amazon_url(url):
            print("⚠️ Invalid Amazon URL format. Must include /dp/ or /gp/product/ and ASIN")
            return
        if not title or not asin:
            fetched_title, fetched_asin = extract_title_and_asin(url)
            title = title or fetched_title
            asin = asin or fetched_asin

        if existing_url:
            print(f"⚠️ Book with this URL already exists (ID: {existing_url[0]})")
            return

        # Check for duplicate ASIN (if provided)
        if asin:
            cursor.execute("SELECT id FROM books WHERE asin = ?", (asin,))
            existing_asin = cursor.fetchone()
            if existing_asin:
                print(f"⚠️ Book with this ASIN already exists (ID: {existing_asin[0]})")
                return

        # Safe to insert
        cursor.execute("""
            INSERT INTO books (title, asin, url, last_price, last_check)
            VALUES (?, ?, ?, NULL, NULL)
        """, (title, asin, url))
        conn.commit()
        print("Book added successfully. ✅")

def remove_book(book_id):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM price_history WHERE book_id = ?", (book_id,))
        cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()


def get_all_books():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, asin, url, last_price, last_check FROM books")
        return cursor.fetchall()

def get_book_by_id(book_id):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, asin, url, last_price, last_check FROM books WHERE id = ?", (book_id,))
        return cursor.fetchone()

def record_price(book_id, price):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO price_history (book_id, price, timestamp)
        VALUES (?, ?, ?)
        """, (book_id, price, datetime.now().isoformat()))
        conn.commit()