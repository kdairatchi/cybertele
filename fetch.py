import os
import json
import time
import requests
import sqlite3
from bs4 import BeautifulSoup
import schedule
import logging
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
import openai

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Set your OpenAI API key
openai.api_key = "YOUR_OPENAI_API_KEY"

# Set your Telegram bot token
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# SQLite Database Setup
DATABASE = 'cybersecurity_data.db'

def setup_database():
    # Connect to the SQLite database and create tables if they do not exist
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS payloads (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  payload TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS vulnerabilities (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  category TEXT,
                  content TEXT
                )''')
    conn.commit()
    conn.close()

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

# Function to fetch and update XSS payloads and other data
def fetch_data():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    for name, urls in SOURCES.items():
        if isinstance(urls, str):
            urls = [urls]
        
        for url in urls:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(strip=True)[:500]  # Save first 500 chars

            # Insert data into vulnerabilities table
            c.execute('INSERT INTO vulnerabilities (category, content) VALUES (?, ?)', (name, text))
    
    conn.commit()
    conn.close()

# Function to handle /start command
def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Hello! I am your cybersecurity bot. Use /fetch to see vulnerabilities or /list_payloads to view XSS payloads.')

# Function to handle /fetch command
def fetch_command(update: Update, _: CallbackContext) -> None:
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id, category, content FROM vulnerabilities')
    rows = c.fetchall()
    conn.close()

    response_text = "🔒 *Latest Cybersecurity Information* 🔒\n\n"
    for row in rows:
        response_text += f"ID: {row[0]}, *{row[1].capitalize()}*\n{row[2]}...\n\n"

    update.message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN)

# Function to handle /list_payloads command
def list_payloads_command(update: Update, _: CallbackContext) -> None:
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id, payload FROM payloads')
    rows = c.fetchall()
    conn.close()

    response_text = "💥 *Stored XSS Payloads* 💥\n\n"
    for row in rows:
        response_text += f"ID: {row[0]}, Payload: {row[1][:100]}...\n"

    update.message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN)

# Function to handle /custom_payload command
def custom_payload_command(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 0:
        update.message.reply_text('Usage: /custom_payload <payload>')
        return

    new_payload = " ".join(context.args)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('INSERT INTO payloads (payload) VALUES (?)', (new_payload,))
    conn.commit()
    conn.close()

    update.message.reply_text('New payload has been added successfully!')

# Function to handle /get_vulnerability command
def get_vulnerability_command(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 0:
        update.message.reply_text('Usage: /get_vulnerability <id>')
        return

    vuln_id = context.args[0]
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT category, content FROM vulnerabilities WHERE id = ?', (vuln_id,))
    row = c.fetchone()
    conn.close()

    if row:
        response_text = f"🔍 *Vulnerability Details* 🔍\nCategory: {row[0]}\nDetails: {row[1]}"
        update.message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN)
    else:
        update.message.reply_text('Vulnerability not found.')

# Function to handle /delete_payload command
def delete_payload_command(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 0:
        update.message.reply_text('Usage: /delete_payload <id>')
        return

    payload_id = context.args[0]
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM payloads WHERE id = ?', (payload_id,))
    conn.commit()
    conn.close()

    update.message.reply_text('Payload has been deleted successfully!')

# Function to schedule regular updates (runs every 24 hours)
def schedule_updates():
    schedule.every(24).hours.do(fetch_data)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Main function to set up the Telegram bot commands
def main() -> None:
    setup_database()

    # Setup the updater and dispatcher for Telegram Bot
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Define bot commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("fetch", fetch_command))
    dispatcher.add_handler(CommandHandler("list_payloads", list_payloads_command))
    dispatcher.add_handler(CommandHandler("custom_payload", custom_payload_command))
    dispatcher.add_handler(CommandHandler("get_vulnerability", get_vulnerability_command))
    dispatcher.add_handler(CommandHandler("delete_payload", delete_payload_command))

    # Start the bot
    updater.start_polling()
    logging.info("Bot is now polling for commands...")

    # Schedule the updates
    schedule_updates()

    # Keep the bot running until interrupted
    updater.idle()

if __name__ == '__main__':
    main()
