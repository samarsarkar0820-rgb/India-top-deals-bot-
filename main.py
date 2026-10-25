import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import sys
import threading
import feedparser
import requests
from telegram import Bot

Environment Variables থেকে তথ্য সংগ্রহ করবে
BOT_TOKEN = os.getenv("8912530871:AAHy_asolgPMREP6st-rC_2HZL1yTbnbs_M")
CHANNEL_ID = os.getenv("@india_top_deals")
CUELINKS_API_KEY = os.getenv("0NA3xXPzaVBi9WrpTjszwjTzxYnyicihZXreV-YCXdY")

POSTED_DEALS_FILE = "posted_deals.txt"


Render Health Check (GET ও HEAD ২টি মেথডই হ্যান্ডেল করবে)
class HealthCheckHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Server is Live!")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        return  # অতিরিক্ত সার্ভার লগ বন্ধ রাখতে


def start_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()


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
    if not CUELINKS_API_KEY:
        return original_url
    api_url = "https://www.cuelinks.com/api/v2/links.json"
    payload = {"url": original_url, "api_key": CUELINKS_API_KEY}
    try:
        res = requests.post(api_url, json=payload, timeout=10)
        if res.status_code in [200, 201]:
            return res.json().get("affiliate_url", original_url)
    except Exception as e:
        print(f"Cuelinks API Error: {e}", flush=True)
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
                    "image": "https://m.media-amazon.com/images/I/61bK6PMOC3L._AC_UF1000,1000_QL80_.jpg",
                }
            )
    return deals


async def run_automation(bot):
    print("🚀 Fully Automatic Telegram Bot Started...", flush=True)
    while True:
        try:
            deals = fetch_latest_deals()
            print(f"Checking deals... Found {len(deals)} new deals.", flush=True)
            for deal in deals:
                affiliate_link = convert_to_cuelinks(deal["link"])
                caption = (
                    f"🔥 TODAY'S BEST DEAL! 🔥\n\n"
                    f"📦 Product: {deal['title']}\n\n"
                    f"🛒 Buy Now: Click Here to Order\n\n"
                    f"📢 Join {CHANNEL_ID} for more offers!"
                )
                await bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=deal["image"],
                    caption=caption,
                    parse_mode="Markdown",
                )
                save_posted_deal(deal["id"])
                print(f"Successfully posted: {deal['title']}", flush=True)
                await asyncio.sleep(180)  # প্রতি পোস্টের মাঝে ৩ মিনিট গ্যাপ
        except Exception as e:
            print(f"Error in automation loop: {e}", flush=True)

        await asyncio.sleep(1800)  # প্রতি ৩০ মিনিট পর নতুন ডিল চেক


def main():
    if not BOT_TOKEN:
        print(
            "❌ ERROR: BOT_TOKEN Environment Variable is missing!", flush=True
        )
        sys.exit(1)

    threading.Thread(target=start_health_server, daemon=True).start()
    bot = Bot(token=BOT_TOKEN)
    asyncio.run(run_automation(bot))


if name == "main":
    main()
    
