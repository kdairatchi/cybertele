import os
import json
import time
import requests
import schedule
import logging
from bs4 import BeautifulSoup
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Set your Telegram bot token
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# Define URLs for scraping cybersecurity information
SOURCES = {
    "xss_payloads": "https://portswigger.net/web-security/cross-site-scripting/cheat-sheet#onanimationstart",
    "directory_listing": [
        "https://portswigger.net/kb/issues/00600100_directory-listing",
        "https://www.invicti.com/learn/directory-listing/"
    ],
    "vulnerabilities": [
        "https://cwe.mitre.org/data/index.html",
        "https://www.cvedetails.com",
        "https://nvd.nist.gov/vuln/",
        "https://cve.mitre.org",
        "https://www.cisa.gov/known-exploited-vulnerabilities-catalog"
    ]
}

# File where we save scraped data
DATA_FILE = "vulnerabilities_data.json"

# Create a function to fetch and update XSS payloads and other data
def fetch_data():
    all_data = {}
    for name, url in SOURCES.items():
        if isinstance(url, str):
            url_list = [url]
        else:
            url_list = url

        all_data[name] = []
        for link in url_list:
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')
            all_data[name].append(soup.get_text(strip=True))

    # Save all fetched data to a file
    with open(DATA_FILE, 'w') as file:
        json.dump(all_data, file, indent=4)

    return all_data

# Function to handle /start command
def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Hello! I am your cybersecurity notification bot. Use /fetch to see the latest vulnerabilities.')

# Function to handle /fetch command
def fetch_command(update: Update, _: CallbackContext) -> None:
    if not os.path.exists(DATA_FILE):
        update.message.reply_text('No data found. Run /update to fetch the latest vulnerabilities.')
        return

    with open(DATA_FILE, 'r') as file:
        data = json.load(file)

    response_text = "🔒 *Latest Cybersecurity Information* 🔒\n\n"
    for category, entries in data.items():
        response_text += f"*{category.capitalize()}*\n"
        for entry in entries:
            response_text += f"{entry[:300]}...\n\n"  # Show only the first 300 chars to avoid overload

    update.message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN)

# Function to handle /update command
def update_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Fetching the latest data...')

    try:
        data = fetch_data()
        update.message.reply_text('Data has been updated successfully!')
    except Exception as e:
        update.message.reply_text(f'Failed to update data: {str(e)}')

# Function to schedule regular updates (runs every 24 hours)
def schedule_updates():
    schedule.every(24).hours.do(fetch_data)

    while True:
        schedule.run_pending()
        time.sleep(1)

# Main function to setup the Telegram bot commands
def main() -> None:
    # Setup the updater and dispatcher for Telegram Bot
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Define bot commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("fetch", fetch_command))
    dispatcher.add_handler(CommandHandler("update", update_command))

    # Start the bot
    updater.start_polling()
    logging.info("Bot is now polling for commands...")
    
    # Schedule the updates
    schedule_updates()

    # Keep the bot running until interrupted
    updater.idle()

if __name__ == '__main__':
    main()
