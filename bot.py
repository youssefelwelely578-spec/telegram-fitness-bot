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

WEBHOOK_PATH = f"/{BOT_TOKEN}"
WEBHOOK_URL = f"https://{RENDER_EXTERNAL_URL}{WEBHOOK_PATH}"

# Initialize Flask
app = Flask(__name__)

# Initialize the Telegram bot application
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Example /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your fitness bot.")

application.add_handler(CommandHandler("start", start))

# Webhook route for Telegram
@app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return jsonify({"status": "ok"})

# Health check route
@app.route("/")
def index():
    return "Bot is running!"

if __name__ == "__main__":
    # Set webhook automatically on startup
    import asyncio

    async def main():
        await application.initialize()
        await application.bot.set_webhook(WEBHOOK_URL)
        await application.start()
        PORT = int(os.environ.get("PORT", 10000))
        app.run(host="0.0.0.0", port=PORT)

    asyncio.run(main())
