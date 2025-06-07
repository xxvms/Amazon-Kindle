import sqlite3
import re
from utils import clean_url

DB_PATH = "books.db"

def clean_existing_urls():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, url FROM books")
        books = cursor.fetchall()

        updated_count = 0
        for book_id, url in books:
            asin_match = re.search(r"/([A-Z0-9]{10})(?:[/?]|$)", url)
            asin = asin_match.group(1) if asin_match else None
            cleaned_url = clean_url(url, asin)
            if cleaned_url and cleaned_url != url:
                cursor.execute("UPDATE books SET url = ? WHERE id = ?", (cleaned_url, book_id))
                updated_count += 1
        conn.commit()
        print(f"✅ Updated {updated_count} URLs in the database.")

if __name__ == "__main__":
    clean_existing_urls()