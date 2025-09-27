import os
import logging
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get your bot token from environment variables (set in Render)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

# Get the public URL of your Render service
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")
if not RENDER_EXTERNAL_URL:
    raise ValueError("RENDER_EXTERNAL_URL environment variable not set!")

# Use a simpler webhook path
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{RENDER_EXTERNAL_URL}{WEBHOOK_PATH}"

# Initialize Flask
app = Flask(__name__)

# Initialize the Telegram bot application
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Example /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your fitness bot.")

application.add_handler(CommandHandler("start", start))

# Webhook route for Telegram - MUST be synchronous for Flask
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    """Handle incoming Telegram updates"""
    try:
        # Process the update
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put(update)
        return jsonify({"status": "ok"})
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return jsonify({"status": "error"}), 500

# Health check route
@app.route("/")
def index():
    return "Bot is running!"

# Set webhook route (optional - for manual webhook setting)
@app.route("/set-webhook")
def set_webhook():
    try:
        # Set webhook
        result = application.bot.set_webhook(WEBHOOK_URL)
        return f"Webhook set successfully: {result}"
    except Exception as e:
        return f"Error setting webhook: {e}"

@app.route("/remove-webhook")
def remove_webhook():
    try:
        result = application.bot.delete_webhook()
        return f"Webhook removed successfully: {result}"
    except Exception as e:
        return f"Error removing webhook: {e}"

if __name__ == "__main__":
    # Set webhook when starting (optional)
    try:
        # Set webhook
        application.bot.set_webhook(WEBHOOK_URL)
        logger.info(f"Webhook set to: {WEBHOOK_URL}")
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
    
    # Start Flask app (Render will set the PORT environment variable)
    PORT = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=PORT, debug=False)
