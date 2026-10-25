import asyncio
import os
import feedparser
import requests
from telegram import Bot

==================== আপনার তথ্যগুলো এখানে দিন ====================
BOT_TOKEN = "8912530871:AAFlJn14vCbhaszkgo5E6s-CX-Zjk4zwmR0"  # আপনার Bot Token বসান
CHANNEL_ID = "@india_top_deals"  # আপনার চ্যানেলের Username বসান
CUELINKS_API_KEY = "Vtz48sGyZuozckO6NhoPelYqsYxRzwija5DbJXMRXCY"  # আপনার Cuelinks API Key বসান
================================================================

POSTED_DEALS_FILE = "posted_deals.txt"
bot = Bot(token=BOT_TOKEN)


def is_already_posted(deal_id):
    """চেক করবে প্রোডাক্টটি আগে পোস্ট করা হয়েছে কিনা"""
    if not os.path.exists(POSTED_DEALS_FILE):
        return False
    with open(POSTED_DEALS_FILE, "r") as f:
        posted = f.read().splitlines()
    return deal_id in posted


def save_posted_deal(deal_id):
    """পোস্ট হওয়া প্রোডাক্ট সেভ করে রাখবে"""
    with open(POSTED_DEALS_FILE, "a") as f:
        f.write(f"{deal_id}\n")


def convert_to_cuelinks(original_url):
    """নরমাল লিংককে Cuelinks Affiliate Link-এ রূপান্তর করে"""
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
    """লাইভ RSS Feed থেকে সেরা অফারের প্রোডাক্ট সংগ্রহ করে"""
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
Affiliate Link তৈরি
                affiliate_link = convert_to_cuelinks(deal["link"])

                caption = (
                    f"🔥 TODAY'S BEST DEAL! 🔥\n\n"
                    f"📦 Product: {deal['title']}\n\n"
                    f"🛒 Buy Now: Click Here to Order\n\n"
                    f"📢 Join {CHANNEL_ID} for more offers!"
                )

Telegram Channels-এ অটো পোস্ট পাঠানো
                await bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=deal["image"],
                    caption=caption,
                    parse_mode="Markdown",
                )

                save_posted_deal(deal["id"])
                print(f"Successfully posted: {deal['title']}")

স্প্যাম রুখতে ৩ মিনিট (১৮০ সেকেন্ড) পর পর পোস্ট করবে
                await asyncio.sleep(180)

        except Exception as e:
            print(f"Error in main loop: {e}")

প্রতি ৩০ মিনিট (১৮০০ সেকেন্ড) পর নতুন ডিল অটো-চেক করবে
        await asyncio.sleep(1800)


if name == "main":
    asyncio.run(run_automation())
                  
