import os
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Get bot token
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set!")

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

# Simple command handler
def start(update, context):
    update.message.reply_text("✅ Hello! I'm your fitness bot. Ready to help you!")

# Add command handler
dispatcher.add_handler(CommandHandler("start", start))

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        logger.info("Received webhook request")
        update = Update.de_json(request.get_json(), bot)
        dispatcher.process_update(update)
        return 'OK'
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return 'ERROR', 500

@app.route('/')
def index():
    return 'Bot is running!'

@app.route('/set_webhook')
def set_webhook():
    webhook_url = "https://telegram-fitness-bot-1.onrender.com/webhook"
    result = bot.set_webhook(webhook_url)
    return f'Webhook set: {result}'

@app.route('/delete_webhook')
def delete_webhook():
    result = bot.delete_webhook()
    return f'Webhook deleted: {result}'

if __name__ == '__main__':
    # Set webhook on startup
    try:
        webhook_url = "https://telegram-fitness-bot-1.onrender.com/webhook"
        bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
    
    # Start Flask app
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
