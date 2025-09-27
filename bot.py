import os
import logging
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

# Initialize
app = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your fitness bot. How can I help you?")

application.add_handler(CommandHandler("start", start))

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        logger.info("Received webhook request")
        update = Update.de_json(request.get_json(), application.bot)
        application.process_update(update)
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
        logger.info(f"Setting webhook to: {webhook_url}")
        
        # Remove existing webhook first
        application.bot.delete_webhook()
        
        # Set new webhook
        result = application.bot.set_webhook(webhook_url)
        
        # Get webhook info to verify
        webhook_info = application.bot.get_webhook_info()
        
        return f'''
        <h1>Webhook Setup</h1>
        <p><strong>Result:</strong> {result}</p>
        <p><strong>Webhook URL:</strong> {webhook_url}</p>
        <p><strong>Current Webhook:</strong> {webhook_info.url}</p>
        <p><strong>Pending Updates:</strong> {webhook_info.pending_update_count}</p>
        <p><strong>Last Error:</strong> {webhook_info.last_error_message}</p>
        '''
    except Exception as e:
        return f"Error setting webhook: {str(e)}"

@app.route('/delete_webhook')
def delete_webhook():
    try:
        result = application.bot.delete_webhook()
        return f'Webhook deleted: {result}'
    except Exception as e:
        return f'Error deleting webhook: {e}'

if __name__ == '__main__':
    # Don't auto-set webhook on startup (do it manually via /set_webhook)
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"Starting bot on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
