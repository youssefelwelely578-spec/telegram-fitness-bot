import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Bot configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

# Create application
application = Application.builder().token(BOT_TOKEN).build()

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text("🎉 Hello! I'm your fitness bot! How can I help you today?")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("🤖 Fitness Bot Help:\n/start - Start the bot\n/help - Show this help")

# Add handlers to application
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))

# Store the application instance for use in webhook
app.config['telegram_app'] = application

@app.route('/')
def index():
    return "🤖 Fitness Bot is running!"

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Webhook endpoint for Telegram"""
    try:
        # Get the application from Flask config
        application = app.config['telegram_app']
        
        # Process the update
        update = Update.de_json(request.get_json(), application.bot)
        await application.process_update(update)
        return "ok"
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return "error", 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Set webhook endpoint"""
    try:
        application = app.config['telegram_app']
        webhook_url = "https://telegram-fitness-bot-1.onrender.com/webhook"
        result = application.bot.set_webhook(webhook_url)
        return f"Webhook set: {result}"
    except Exception as e:
        return f"Error setting webhook: {e}"

@app.route('/delete_webhook', methods=['GET'])
def delete_webhook():
    """Delete webhook endpoint"""
    try:
        application = app.config['telegram_app']
        result = application.bot.delete_webhook()
        return f"Webhook deleted: {result}"
    except Exception as e:
        return f"Error deleting webhook: {e}"

if __name__ == '__main__':
    # Initialize the application
    application = app.config['telegram_app']
    
    # Set webhook on startup
    webhook_url = "https://telegram-fitness-bot-1.onrender.com/webhook"
    application.bot.set_webhook(webhook_url)
    logger.info(f"Webhook set to: {webhook_url}")
    
    # Start Flask app
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
