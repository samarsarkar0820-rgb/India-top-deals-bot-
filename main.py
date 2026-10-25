import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import threading
import feedparser
import requests
from telegram import Bot

# ==================== আপনার তথ্যগুলো দিন ====================
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
CHANNEL_ID = "@your_channel_username"
CUELINKS_API_KEY = "YOUR_CUELINKS_API_KEY"
# ==========================================================

POSTED_DEALS_FILE = "posted_deals.txt"
bot = Bot(token=BOT_TOKEN)


# Render Free Web Service Active রাখার জন্য Web Server
class HealthCheckHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running Successfully!")


def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()


# ব্যাকগ্রাউন্ডে সার্ভার চালু রাখা
threading.Thread(target=run_dummy_server, daemon=True).start()


def is_already_posted(deal_id):
    if not os.path.exists(POSTED_DEALS_FILE):
        return False
    with open(POSTED_DEALS_FILE, "r") as f:
        posted = f.read().splitlines()
    return deal_id in posted


def save_posted_deal(deal_id):
    with open(POSTED_DEALS_FILE, "a") as f:
        f.write(f"{deal_id}\n")


def convert_to_cuelinks(original_url):
    api_url = "https://www.cuelinks.com/api/v2/links.json"
    payload = {"url": original_url, "api_key": CUELINKS_API_KEY}
    try:
        res = requests.post(api_url, json=payload, timeout=10)
        if res.status_code in [200, 201]:
            return res.json().get("affiliate_url", original_url)
    except Exception as e:
        print(f"Cuelinks API Error: {e}")
    return original_url


def fetch_latest_deals():
    feed_url = "https://www.desidime.com/rss/promoted_deals.rss"
    feed = feedparser.parse(feed_url)

    deals = []
    for entry in feed.entries[:10]:
        deal_id = entry.id if hasattr(entry, "id") else entry.link
        if not is_already_posted(deal_id):
            deals.append(
                {
                    "id": deal_id,
                    "title": entry.title,
                    "link": entry.link,
                    "image": "https://via.placeholder.com/600x400.png?text=Hot+Deal",
                }
            )
    return deals


async def run_automation():
    print("🚀 Fully Automatic Telegram Bot Started...")
    while True:
        try:
            deals = fetch_latest_deals()
            for deal in deals:
                affiliate_link = convert_to_cuelinks(deal["link"])

                caption = (
                    f"🔥 **TODAY'S BEST DEAL!** 🔥\n\n"
                    f"📦 **Product:** {deal['title']}\n\n"
                    f"🛒 **Buy Now:** [Click Here to Order]({affiliate_link})\n\n"
                    f"📢 Join {CHANNEL_ID} for more offers!"
                )

                await bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=deal["image"],
                    caption=caption,
                    parse_mode="Markdown",
                )

                save_posted_deal(deal["id"])
                print(f"Successfully posted: {deal['title']}")

                await asyncio.sleep(180)

        except Exception as e:
            print(f"Error in main loop: {e}")

        await asyncio.sleep(1800)


if __name__ == "__main__":
    asyncio.run(run_automation())
  
