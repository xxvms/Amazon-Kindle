from db import get_all_books, update_book_price, record_price
import requests
from bs4 import BeautifulSoup
from time import sleep
from random import uniform

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0 Safari/537.36"
    )
}

def get_kindle_price(url):
    try:
        print(f"Fetching: {url}")

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        # # Just for debugging: save the page to disk
        with open("debug.html", "w", encoding="utf-8") as f:
             f.write(soup.prettify())
        print("📝 Saved debug.html")

        # Strategy 1: Find "Kindle Edition Format:" and locate price
        kindle_label = soup.find("span", attrs={"aria-label": "Kindle Edition Format:"})
        if kindle_label:
            slot_price = kindle_label.find_next("span", class_="slot-price")
            if slot_price:
                price_span = slot_price.find("span", class_='a-color-price')
                if price_span:
                    return price_span.text.strip()
        # Strategy 2: fallback search (still basic)
        fallback_prices = soup.find_all("span", string=lambda t: t and "£" in t)
        for span in fallback_prices:
            if "kindle" in span.find_parent().text.lower():
                return span.text.strip()

        # Strategy 3: Look for "Kindle Price:" label then find the next price span
        label = soup.find("span", string="Kindle Price:")
        if label:
            price_span = label.find_next("span", class_="a-color-price")
            if price_span:
                return price_span.text.strip()
        # Strategy 4: Extract real purchase price from slot-price block, skip £0.00 if others are available
        slot_prices = soup.find_all("span", class_="slot-price")
        for slot in slot_prices:
            price_spans = [span for span in slot.find_all("span", class_="a-color-price", recursive=False)]
            valid_prices = [
                span.get_text(strip=True)
                for span in price_spans
                if "£" in span.get_text(strip=True)
            ]
            non_zero_prices = [p for p in valid_prices if p != "£0.00"]
            if non_zero_prices:
                return non_zero_prices[0]
            elif valid_prices:
                return valid_prices[0]

        # Strategy 5: Check inside kindleExtraMessage block
        extra_msg_block = soup.find("span", class_="kindleExtraMessage")
        if extra_msg_block:
            alt_price = extra_msg_block.find("span", class_="a-color-price")
            if alt_price:
                text = alt_price.get_text(strip=True)
                if "£" in text:
                    return text

        return None

    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return None


def main():
    books = get_all_books()
    if not books:
        print("No books to check.")
        return

    print(f"Found {len(books)} book(s) to check:")
    for book in books:
        book_id, title, asin, url, *_ = book
        print(f"[{book_id}] {title or '(No title)'} -> {url}")

        price_str = get_kindle_price(url)
        if price_str:
            print(f"✅ Price found: {price_str}")
            # Try parsing price as float (strip £)
            try:
                price_value = float(price_str.replace("£", "").strip())
                update_book_price(book_id,price_value)
                record_price(book_id, price_value)
                print(f"💾 Updated database with £{price_value}")
            except ValueError:
                print(f"⚠️ Could not parse price string: {price_str}")
        else:
            print(f"⚠️ Price not found")
        sleep(uniform(1.5, 3.0))



if __name__ == "__main__":
    main()