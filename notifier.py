#  notifier.py  —  Sends email alerts via Gmail SMTP

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import SENDER_EMAIL, APP_PASSWORD, RECEIVER_EMAIL


def send_alert(product_name: str, url: str, current_price: float, previous_low: float):
    """
    Sends a price drop alert email via Gmail's SMTP server.

    HOW SMTP WORKS:
    ┌────────────┐       TLS/587        ┌──────────────────┐       ┌──────────┐
    │ Your Script│ ──────────────────▶  │ smtp.gmail.com   │ ────▶ │ Inbox    │
    └────────────┘   (encrypted tunnel) └──────────────────┘       └──────────┘

    Port 587 = STARTTLS (starts plain, upgrades to encrypted)
    Port 465 = SSL/TLS  (encrypted from the start)
    We use 587 — it's the modern standard.

    WHY APP PASSWORD and not your real password:
    Google blocks "less secure" sign-ins. An App Password is a
    16-character token that only works for one specific app.
    Even if someone steals it, they can only send email — not
    access your account.
    """
    drop_amount = previous_low - current_price
    drop_percent = (drop_amount / previous_low) * 100

    subject = f"🔔 Price Drop Alert: {product_name} — Now £{current_price:.2f}!"

    # --- Build a nice HTML email body ---
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
        <div style="background: #f0f7ff; padding: 20px; border-radius: 8px;">
            <h2 style="color: #1a73e8;">💰 Price Drop Detected!</h2>
            <p style="font-size: 16px;">Good news! <strong>{product_name}</strong> has dropped in price.</p>

            <table style="width:100%; border-collapse: collapse; margin: 20px 0;">
                <tr style="background: #fff;">
                    <td style="padding:12px; border:1px solid #ddd;">Previous Lowest Price</td>
                    <td style="padding:12px; border:1px solid #ddd; text-decoration:line-through; color:#999;">
                        £{previous_low:.2f}
                    </td>
                </tr>
                <tr style="background: #e8f5e9;">
                    <td style="padding:12px; border:1px solid #ddd;"><strong>Current Price</strong></td>
                    <td style="padding:12px; border:1px solid #ddd; color:#2e7d32; font-size:20px;">
                        <strong>£{current_price:.2f}</strong>
                    </td>
                </tr>
                <tr style="background: #fff;">
                    <td style="padding:12px; border:1px solid #ddd;">You Save</td>
                    <td style="padding:12px; border:1px solid #ddd; color:#c62828;">
                        £{drop_amount:.2f} ({drop_percent:.1f}% off!)
                    </td>
                </tr>
            </table>

            <a href="{url}"
               style="display:inline-block; padding:12px 24px; background:#1a73e8;
                      color:white; text-decoration:none; border-radius:4px; font-size:16px;">
                👉 View Product
            </a>

            <p style="margin-top:24px; color:#666; font-size:12px;">
                This alert was sent by your PriceTracker bot. 🤖
            </p>
        </div>
    </body>
    </html>
    """

    # --- Plain text fallback (for email clients that don't render HTML) ---
    plain_body = (
        f"Price Drop Alert: {product_name}\n"
        f"Previous Low: £{previous_low:.2f}\n"
        f"Current Price: £{current_price:.2f}\n"
        f"You save: £{drop_amount:.2f} ({drop_percent:.1f}% off!)\n"
        f"Link: {url}"
    )

    # --- Assemble the email ---
    msg = MIMEMultipart("alternative")  # "alternative" = send both plain + HTML
    msg["Subject"] = subject
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECEIVER_EMAIL
    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))   # Email clients prefer HTML if available

    # --- Connect to Gmail and send ---
    try:
        print(f"  [→] Connecting to Gmail SMTP...")
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()          # Identify ourselves to the server
            server.starttls()      # Upgrade connection to encrypted TLS
            server.ehlo()          # Re-identify after TLS upgrade
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())

        print(f"  [✓] Alert email sent to {RECEIVER_EMAIL}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("  [✗] Gmail authentication failed!")
        print("      → Make sure you're using an App Password, not your real password.")
        print("      → Guide: myaccount.google.com → Security → App Passwords")
        return False
    except smtplib.SMTPException as e:
        print(f"  [✗] SMTP error: {e}")
        return False
    except Exception as e:
        print(f"  [✗] Unexpected error sending email: {e}")
        return False


def send_summary(results: list[dict]):
    """
    Sends a daily summary email with all tracked products and their prices.
    Called at the end of each tracking run.
    """
    subject = "📊 PriceTracker Daily Summary"

    rows_html = ""
    rows_plain = ""
    for r in results:
        status = "✅ New Low!" if r.get("is_new_low") else "—"
        rows_html += f"""
        <tr>
            <td style="padding:8px;border:1px solid #ddd;">{r['name']}</td>
            <td style="padding:8px;border:1px solid #ddd;">£{r['price']:.2f}</td>
            <td style="padding:8px;border:1px solid #ddd;">£{r['lowest']:.2f}</td>
            <td style="padding:8px;border:1px solid #ddd;">{status}</td>
        </tr>"""
        rows_plain += f"  {r['name']}: £{r['price']:.2f} (Lowest: £{r['lowest']:.2f}) {status}\n"

    html_body = f"""
    <html><body style="font-family:Arial,sans-serif;max-width:700px;margin:auto;">
        <h2>📊 PriceTracker Daily Summary</h2>
        <table style="width:100%;border-collapse:collapse;">
            <thead style="background:#1a73e8;color:white;">
                <tr>
                    <th style="padding:10px;text-align:left;">Product</th>
                    <th style="padding:10px;">Today's Price</th>
                    <th style="padding:10px;">All-Time Low</th>
                    <th style="padding:10px;">Status</th>
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECEIVER_EMAIL
    msg.attach(MIMEText(f"Daily Summary:\n{rows_plain}", "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print(f"  [✓] Daily summary sent to {RECEIVER_EMAIL}")
    except Exception as e:
        print(f"  [✗] Could not send summary: {e}")