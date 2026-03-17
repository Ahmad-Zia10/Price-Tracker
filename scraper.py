#  scraper.py  —  Fetches the webpage and extracts the price

import requests
from bs4 import BeautifulSoup
from config import HEADERS
 
# Add new sites here as you discover their price elements.
# "domain"  →  (html_tag, css_class)
# Where the price lives at each site.
SITE_SELECTORS = {
    "books.toscrape.com": ("p",    "price_color",  None),
    "amazon.in":          ("span", "a-price-whole", None),
    "flipkart.com":       ("div",  "v1zwn21k",      None),
    "myntra.com":         ("span", "pdp-price",     "strong"),  # ← third value = child tag
}


def detect_selector(url : str) :
    """Checks given url against the selecctors list and finds out which site to scrape to determine the correct 
    tag name and class name to target and get the price"""

    for domain, selector in SITE_SELECTORS.items():
        if domain in url:
            return selector
    return None

def get_price(url: str) -> float | None:
    """
    Visits a product URL, auto-detects the site, and extracts the price.
    """
    #   Detect which site this is
    selector = detect_selector(url)

    if selector is None:
        print(f"  [!] Unrecognised site. Supported: {', '.join(SITE_SELECTORS.keys())}")
        return None

    tag, css_class = selector

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        price_tag = soup.find(tag, class_=css_class)

        if not price_tag:
            print(f"  [!] Price element not found on page.")
            print(f"      The site may have updated its HTML. Check scraper.py → SITE_SELECTORS.")
            return None

        raw = price_tag.text.strip()
        cleaned = "".join(ch for ch in raw if ch.isdigit() or ch == ".")
        return float(cleaned)

    except requests.exceptions.Timeout:
        print(f"  [!] Request timed out.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"  [!] Network error: {e}")
        return None
    except ValueError as e:
        print(f"  [!] Could not parse price: {e}")
        return None


def get_product_title(url: str) -> str:
    """
    Fetches the product title from the page.
    Used to double-check we scraped the right product.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        title_tag = soup.find("h1")
        return title_tag.text.strip() if title_tag else "Unknown Product"
    except Exception:
        return "Unknown Product"