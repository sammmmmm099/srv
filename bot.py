import logging
import os
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from dotenv import load_dotenv
import asyncio
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

client = None
proxy = None
user_stats = {}

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start_telethon_session(phone_number):
    global client
    api_id = os.getenv('API_ID')
    api_hash = os.getenv('API_HASH')
    client = TelegramClient('session_name', api_id, api_hash)
    try:
        await client.start(phone_number)
        return True
    except SessionPasswordNeededError:
        logger.error("2FA enabled.")
        return False
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return False

def request_phone_number(update: Update, context: CallbackContext):
    update.message.reply_text("Send your phone number to login.")

def handle_phone_number(update: Update, context: CallbackContext):
    phone_number = update.message.text.strip()
    update.message.reply_text("Logging in...")
    success = asyncio.run(start_telethon_session(phone_number))
    update.message.reply_text("Login successful!" if success else "Login failed.")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome! Use /login to begin.")

def batch(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Provide a link to download media from.")
        return
    link = context.args[0]
    update.message.reply_text(f"Downloading from: {link}")
    update.message.reply_text("Download/upload complete.")

def setproxy(update: Update, context: CallbackContext):
    global proxy
    if not context.args:
        update.message.reply_text("Provide proxy address.")
        return
    proxy = context.args[0]
    update.message.reply_text(f"Proxy set to: {proxy}")

def pay(update: Update, context: CallbackContext):
    update.message.reply_text("Premium granted for 1 day!")

def stats(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    stats = user_stats.get(user_id, {'messages': 0, 'media': 0})
    update.message.reply_text(f"Stats:\nMessages: {stats['messages']}\nMedia: {stats['media']}")

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text("""Commands:
/start
/login
/setbot
/batch <link>
/setproxy <addr>
/pay
/stats
/help
/rembot
/remproxy
/logout
""")

def rembot(update: Update, context: CallbackContext):
    update.message.reply_text("Bot removed.")

def remproxy(update: Update, context: CallbackContext):
    global proxy
    proxy = None
    update.message.reply_text("Proxy removed.")

def logout(update: Update, context: CallbackContext):
    global client
    if client:
        client.disconnect()
        update.message.reply_text("Logged out.")
    else:
        update.message.reply_text("No active session.")

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("login", request_phone_number))
    dp.add_handler(CommandHandler("setbot", lambda u, c: u.message.reply_text("Bot setup complete.")))
    dp.add_handler(CommandHandler("batch", batch))
    dp.add_handler(CommandHandler("setproxy", setproxy))
    dp.add_handler(CommandHandler("pay", pay))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("rembot", rembot))
    dp.add_handler(CommandHandler("remproxy", remproxy))
    dp.add_handler(CommandHandler("logout", logout))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
