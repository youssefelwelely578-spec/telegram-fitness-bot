import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --------------------
# Configuration
# --------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Make sure Render has BOT_TOKEN set
PORT = int(os.environ.get("PORT", 10000))  # Render provides this environment variable

WEBHOOK_PATH = f"/{BOT_TOKEN}"
WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_URL')}{WEBHOOK_PATH}"  # Render app URL

# --------------------
# Initialize bot
# --------------------
application = ApplicationBuilder().token(BOT_TOKEN).build()

# --------------------
# Command handlers
# --------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your fitness bot 🚀")

application.add_handler(CommandHandler("start", start))

# --------------------
# Flask app for webhook
# --------------------
app = Flask(__name__)

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    """Receives updates from Telegram"""
    update = Update.de_json(request.get_json(force=True), application.bot)
    # Schedule processing of the update in the running event loop
    application.create_task(application.process_update(update))
    return "OK"

# --------------------
# Set webhook when starting
# --------------------
async def set_webhook():
    await application.bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook set to: {WEBHOOK_URL}")

if __name__ == "__main__":
    import asyncio
    # Initialize bot before running Flask
    asyncio.run(set_webhook())
    # Start Flask server
    app.run(host="0.0.0.0", port=PORT)

