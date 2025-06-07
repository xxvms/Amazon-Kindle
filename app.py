from flask import Flask, render_template, request, redirect, url_for, flash
from db import get_all_books, add_book, remove_book, get_book_by_id, update_book_price, record_price
from datetime import datetime
from utils import is_valid_amazon_url, extract_title_and_asin
import requests
from bs4 import BeautifulSoup
import re
from scraper import get_kindle_price


app = Flask(__name__)
app.secret_key = "my_secret_key"

@app.template_filter("format_datetime")
def format_datetime(value):
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime("%H:%M %d/%m/%y")
    except Exception:
        return value

@app.route("/")
def home():
    books = get_all_books()
    return render_template("index.html", books=books)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        url = request.form["url"].strip()
        title = request.form.get("title") or None
        asin = request.form.get("asin") or None
        # Auto-fetch if missing
        if not title or not asin:
            fetched_title, fetched_asin = extract_title_and_asin(url)
            title = title or fetched_title
            asin = asin or fetched_asin

            if not title or not asin:
                flash("❌ Could not extract title or ASIN from the provided Amazon URL.")
                return redirect(url_for("add"))
        if not is_valid_amazon_url(url):
            flash("❌ Invalid Amazon URL. Please provide a direct link to a Kindle book.")
            return redirect(url_for("add"))

        add_book(url=url, title=title, asin=asin)
    return render_template("add.html")

@app.route("/delete/<int:book_id>", methods=["POST"])
def delete(book_id):
    print(f"🔥 DELETE TRIGGERED for book ID: {book_id}")
    import sys; sys.stdout.flush()

    book = get_book_by_id(book_id)
    if book:
        remove_book(book_id)
        flash(f"Deleted book: {book[1] or '(Untitled)'}")
    else:
        flash("Book not found")
    return redirect(url_for("home"))

@app.route("/check-prices")
def check_prices():
    books = get_all_books()
    updated = []

    for book in books:
        book_id, title, asin, url, *_ = book
        price_str = get_kindle_price(url)
        if price_str:
            try:
                price_value = float(price_str.replace("£", "").strip())
                update_book_price(book_id, price_value)
                record_price(book_id, price_value)
                updated.append((title or "(No title", price_value))
            except ValueError:
                pass
    flash(f"✅ Checked prices for {len(updated)} book(s).")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)