#!/usr/bin/env python3
# ============================================================
#  manage.py  —  Add, remove, and list tracked products
#
#  Usage:
#    python manage.py list           → show all tracked products
#    python manage.py add            → add a new product (interactive)
#    python manage.py remove         → remove a product (interactive)
# ============================================================

import json
import os
import sys
from config import PRODUCTS_FILE


# Helpers

def load_products() -> list:
    """Read products from JSON file. Returns empty list if file doesn't exist."""
    if not os.path.exists(PRODUCTS_FILE):
        return []
    with open(PRODUCTS_FILE, "r") as f:   #implementation of context manager. Bascially automates resource management.Automatically closes the file when code bloack has finished or error is encountered. 
        return json.load(f) #read json data from a file and convert into pyhton object, dict or list.


def save_products(products: list):
    """Write products list back to JSON file, nicely formatted."""
    with open(PRODUCTS_FILE, "w") as f: 
        json.dump(products, f, indent=4) # converts python object into json foramt and wrties them in the file. indent = 4 : just a formatting attribute, makes file readable easily.


# Commands 

def list_products():
    """Print all currently tracked products in a readable table."""
    products = load_products()

    if not products:
        print("\n  No products are being tracked yet.")
        print("  Run: python manage.py add\n")
        return

    print(f"\n  {'#':<4} {'Name':<30} {'Target £':>10}  URL")
    print("  " + "─" * 75)
    for i, p in enumerate(products, 1):
        url_short = p['url'][:45] + "..." if len(p['url']) > 45 else p['url']
        print(f"  {i:<4} {p['name']:<30} £{p['target_price']:>8.2f}  {url_short}")
    print(f"\n  Total: {len(products)} product(s) tracked.\n")


def add_product():
    """Interactively prompt the user for a new product and save it."""
    print("\n Add a new product ")
    print("  (Press Ctrl+C at any time to cancel)\n")

    try:
        # Get product name
        name = input("  Product name (e.g. 'iPhone 15'): ").strip()
        if not name:
            print("  [!] Name cannot be empty.")
            return

        # Check for duplicates
        products = load_products()
        existing_names = [p['name'].lower() for p in products]
        if name.lower() in existing_names:
            print(f"  [!] '{name}' is already being tracked.")
            return

        # --- Get URL ---
        url = input("  Product URL: ").strip()
        if not url.startswith("http"):
            print("  [!] URL must start with http:// or https://")
            return

        # --- Get target price ---
        while True:
            try:
                raw = input("  Alert me when price drops below £: ").strip()
                target_price = float(raw)
                if target_price <= 0:
                    print("  [!] Price must be greater than 0.")
                    continue
                break
            except ValueError:
                print("  [!] Please enter a number (e.g. 29.99)")

        # --- Confirm ---
        print(f"\n  Adding:")
        print(f"    Name:         {name}")
        print(f"    URL:          {url[:60]}{'...' if len(url) > 60 else ''}")
        print(f"    Alert below:  £{target_price:.2f}")
        confirm = input("\n  Confirm? (y/n): ").strip().lower()

        if confirm != 'y':
            print("  Cancelled.")
            return

        # --- Save ---
        products.append({
            "name": name,
            "url": url,
            "target_price": target_price
        })
        save_products(products)
        print(f"\n  [✓] '{name}' added successfully!")
        print(f"      Run 'python tracker.py' to check its price now.\n")

    except KeyboardInterrupt:
        print("\n\n  Cancelled.\n")


def remove_product():
    """Show a numbered list and let the user pick which product to remove."""
    products = load_products()

    if not products:
        print("\n  No products to remove.\n")
        return

    print("\n Remove a product \n")
    for i, p in enumerate(products, 1):
        print(f"  {i}. {p['name']}  (£{p['target_price']:.2f})")

    print()
    try:
        raw = input(f"  Enter number to remove (1–{len(products)}), or 0 to cancel: ").strip()
        choice = int(raw)

        if choice == 0:
            print("  Cancelled.\n")
            return

        if not 1 <= choice <= len(products):
            print(f"  [!] Invalid choice. Enter a number between 1 and {len(products)}.")
            return

        removed = products.pop(choice - 1)
        save_products(products)
        print(f"\n  [✓] '{removed['name']}' removed.\n")

    except ValueError:
        print("  [!] Please enter a number.")
    except KeyboardInterrupt:
        print("\n\n  Cancelled.\n")


# Entry point 

COMMANDS = {
    "list":   list_products,
    "add":    add_product,
    "remove": remove_product,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("\n  Usage:")
        print("    python manage.py list      — show all tracked products")
        print("    python manage.py add       — add a new product")
        print("    python manage.py remove    — remove a product\n")
        sys.exit(1)

    COMMANDS[sys.argv[1]]()
