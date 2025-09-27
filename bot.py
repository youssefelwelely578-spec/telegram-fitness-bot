import os
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import openai
import asyncio

# -------------------------------
# Configuration
# -------------------------------
TOKEN = os.environ.get("TELEGRAM_TOKEN")
PORT = int(os.environ.get("PORT", 10000))
openai.api_key = os.environ.get("OPENAI_API_KEY")

# -------------------------------
# Logging
# -------------------------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# -------------------------------
# Flask app
# -------------------------------
app = Flask(__name__)

# -------------------------------
# Telegram Application
# -------------------------------
application = Application.builder().token(TOKEN).build()

# -------------------------------
# OpenAI helper
# -------------------------------
def get_ai_text(user_input: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": user_input}],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"OpenAI Error: {e}")
        return "Sorry, I'm having trouble generating a response right now."

# -------------------------------
# Telegram Handlers
# -------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I'm your AI personal trainer 🤖💪\nAsk me any fitness question!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    logging.info(f"User: {user_text}")
    ai_response = get_ai_text(user_text)
    await update.message.reply_text(ai_response)

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# -------------------------------
# Webhook route
# -------------------------------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), Bot(TOKEN))
    asyncio.run(application.process_update(update))
    return "OK", 200

# -------------------------------
# Run Flask
# -------------------------------
if __name__ == "__main__":
    logging.info("Bot is starting...")
    app.run(host="0.0.0.0", port=PORT)

