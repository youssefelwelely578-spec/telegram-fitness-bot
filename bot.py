import os
import logging
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import openai

# --- CONFIG ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # set in Render
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # set in Render
PORT = int(os.environ.get("PORT", "10000"))

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

# --- FLASK APP ---
app = Flask(__name__)

# --- TELEGRAM BOT APP ---
application = ApplicationBuilder().token(BOT_TOKEN).build()

# --- OPENAI SETUP ---
openai.api_key = OPENAI_API_KEY

async def get_ai_text(prompt: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI Error: {e}")
        return "Sorry, something went wrong with the AI."

# --- TELEGRAM HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me a message and I will answer using OpenAI GPT-5 Mini.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    reply = await get_ai_text(user_text)
    await update.message.reply_text(reply)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- WEBHOOK ENDPOINT ---
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        asyncio.run(application.process_update(update))
    except Exception as e:
        logger.exception(f"Webhook processing error: {e}")
    return jsonify({"status": "ok"})

# --- HEALTH CHECK ---
@app.route("/", methods=["GET"])
def index():
    return "Bot is running"

# --- RUN ---
if __name__ == "__main__":
    logger.info(f"Starting Flask server on port {PORT}")
    app.run(host="0.0.0.0", port=PORT)
