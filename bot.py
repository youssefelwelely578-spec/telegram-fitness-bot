import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import openai

# ---------- CONFIG ----------
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # your Telegram bot token
OPENAI_KEY = os.environ.get("OPENAI_KEY")  # your OpenAI API key
PORT = int(os.environ.get("PORT", 10000))

openai.api_key = OPENAI_KEY

# ---------- LOGGING ----------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------- FLASK ----------
app = Flask(__name__)

# ---------- TELEGRAM ----------
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Example start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your fitness bot. Send me a message and I'll reply using GPT-5-mini.")

# Example text handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": user_text}]
        )
        answer = response['choices'][0]['message']['content']
    except Exception as e:
        logger.error(f"OpenAI Error: {e}")
        answer = "Sorry, something went wrong with OpenAI."

    await update.message.reply_text(answer)

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ---------- FLASK ROUTE ----------
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    """Telegram webhook route."""
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    asyncio.run(application.process_update(update))
    return "ok"

@app.route("/")
def index():
    return "Bot is running!"

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)

