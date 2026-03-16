
# Use manage.py to add, remove, and list products:
#   python manage.py add
#   python manage.py remove
#   python manage.py list

PRODUCTS_FILE = "products.json"

# Email Settings
# Step 1: Enable 2FA on your Google account
# Step 2: Go to myaccount.google.com → Security → App Passwords
# Step 3: Generate an App Password for "Mail"
# Step 4: Paste it below (looks like: abcd efgh ijkl mnop)

SENDER_EMAIL    = "your_gmail@gmail.com"
APP_PASSWORD    = "xxxx xxxx xxxx xxxx"          
RECEIVER_EMAIL  = "your_gmail@gmail.com"         

#File Settings 
CSV_FILE = "prices.csv"

# Scraper Settings 
# Pretend to be a real browser so sites don't block us
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}