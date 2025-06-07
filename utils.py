import re
import requests
from bs4 import BeautifulSoup

def is_valid_amazon_url(url):
    return bool(re.match(r"^https://(www\.)?amazon\.co\.uk/.*/(dp|gp/product)/[A-Z0-9]{10}", url))

def extract_title_and_asin(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0 Safari/537.36"
        )
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "lxml")

        # Title: look for product Title
        tile_tag = soup.find("span", id="productTitle")
        title = tile_tag.get_text() if tile_tag else None
        if title:
            title = re.sub(r"\s+", " ", title).strip() # normalize spaces
            title = re.sub(r"\s*\bKindle Edition\b\s*", "", title, flags=re.IGNORECASE)
            title = re.sub(r"\s*\|\s*$", "", title)

        # ASIN: try to get from URL or HTML
        asin = None
        match = re.search(r"/(?:dp|gp/aw/d|gp/product)/([A-Z0-9]{10})", url)
        if match:
            asin = match.group(1)
        else:
            asin_meta = soup.find("input", {"name": "ASIN"})
            if asin_meta and asin_meta.get("value"):
                asin = asin_meta["value"]
        return title, asin
    except Exception as e:
        print(f"⚠️ Failed to extract title/ASIN: {e}")
        return None, None

def get_ereaderiq_url(asin):
    if asin:
        return f"https://uk.ereaderiq.com/dp/{asin}/"
    return None

def clean_url(url, asin=None):
    if not asin:
        match = re.search(r"/([A-Z0-9]{10})(?:[/?]|$)", url)
        asin = match.group(1) if match else None
    if asin:
        return f"https://www.amazon.co.uk/dp/{asin}"
    return url