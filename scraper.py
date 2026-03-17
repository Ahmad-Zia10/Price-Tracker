#  scraper.py  —  Fetches the webpage and extracts the price

import requests
from bs4 import BeautifulSoup
from config import HEADERS


def get_price(url: str) -> float | None:
    """
    Visits a product URL and returns the price as a float.
    """
    try:
        # Download the page 
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()  # Raises an error for 4xx/5xx HTTP codes

        # Parse the HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the price element
        # On books.toscrape.com the price lives in: <p class="price_color">£51.77</p>
        # On Amazon it would be: <span class="a-price-whole"> etc.
        # You adapt this one line per site — everything else stays the same!
        price_tag = soup.find("p", class_="price_color") 

        if not price_tag:
            print(f"  [!] Price element not found at {url}")
            return None

        # Clean and convert
        # price_tag.text might look like "£51.77" or "Â£51.77"
        raw = price_tag.text.strip()
        # Remove any non-numeric characters except the decimal point
        cleaned = "".join(ch for ch in raw if ch.isdigit() or ch == ".")
        return float(cleaned)

    except requests.exceptions.Timeout:
        print(f"  [!] Request timed out for {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"  [!] Network error: {e}")
        return None
    except ValueError as e:
        print(f"  [!] Could not convert price to number: {e}")
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