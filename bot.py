import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN")
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "telegram-fitness-bot-1.onrender.com")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

# Initialize Flask
app = Flask(__name__)

# Initialize the Telegram application
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Hello! I'm your fitness bot. How can I help you today?")

# Add command handler
application.add_handler(CommandHandler("start", start))

# Initialize the application
async def initialize_app():
    await application.initialize()
    await application.start()
    await application.updater.start_polling()  # This initializes the update processing

# Run initialization when the app starts
@app.before_first_request
def initialize():
    """Initialize the bot application before handling any requests"""
    try:
        # Initialize the application
        asyncio.run(initialize_app())
        logger.info("Bot application initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing bot: {e}")

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        logger.info("Received webhook request")
        update = Update.de_json(request.get_json(), application.bot)
        
        # Process the update through the application
        asyncio.create_task(application.process_update(update))
        
        return 'OK'
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return 'ERROR', 500

@app.route('/')
def index():
    return 'Bot is running!'

@app.route('/set_webhook')
def set_webhook():
    try:
        webhook_url = f"https://{RENDER_EXTERNAL_URL}/webhook"
        result = application.bot.set_webhook(webhook_url)
        return f'Webhook set: {result} to {webhook_url}'
    except Exception as e:
        return f'Error setting webhook: {e}'

if __name__ == '__main__':
    # Initialize the bot application
    try:
        asyncio.run(initialize_app())
        logger.info("Bot application initialized")
    except Exception as e:
        logger.error(f"Initialization error: {e}")
    
    # Set webhook
    webhook_url = f"https://{RENDER_EXTERNAL_URL}/webhook"
    application.bot.set_webhook(webhook_url)
    logger.info(f"Webhook set to: {webhook_url}")
    
    # Start Flask
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
