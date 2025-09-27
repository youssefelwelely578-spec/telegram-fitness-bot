import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # must match Render env variable
PORT = int(os.environ.get("PORT", 10000))

# Flask app
app = Flask(__name__)

# Telegram bot application
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Example command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your bot.")

application.add_handler(CommandHandler("start", start))

# Initialize Telegram bot application
async def init_app():
    await application.initialize()
    await application.start()
    # Not using polling; webhook only
    # await application.updater.start_polling()  # optional

# Run initialization before Flask handles requests
asyncio.run(init_app())

# Webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    # Schedule async processing without blocking Flask
    asyncio.create_task(application.process_update(update))
    return "ok"

# Run Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
