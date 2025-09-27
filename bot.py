import os
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import openai
import logging

# -----------------------
# Configuration
# -----------------------
PORT = int(os.environ.get("PORT", 10000))
BOT_TOKEN = "8426717766:AAGeYeMKt4wetni8l85LyUx_PsdnTF5Ue5E"
OPENAI_API_KEY = "sk-...8iIA"  # Your OpenAI key

# -----------------------
# Logging
# -----------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# -----------------------
# OpenAI setup
# -----------------------
openai.api_key = OPENAI_API_KEY

async def get_ai_text(prompt: str) -> str:
    try:
        logging.info(f"Sending prompt to OpenAI: {prompt}")
        response = openai.ChatCompletion.create(
            model="gpt-5-mini",  # or "gpt-5" if available
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.choices[0].message.content
        logging.info(f"OpenAI response: {text}")
        return text
    except Exception as e:
        logging.error(f"OpenAI Error: {e}")
        return "Sorry, I could not process your request."

# -----------------------
# Telegram setup
# -----------------------
app = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me a message and I'll respond using AI.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    ai_response = await get_ai_text(user_message)
    await update.message.reply_text(ai_response)

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# -----------------------
# Webhook route
# -----------------------
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    # Schedule processing in the running event loop
    asyncio.create_task(application.process_update(update))
    return "OK"

# -----------------------
# Health check
# -----------------------
@app.route("/", methods=["GET"])
def index():
    return "Bot is running."

# -----------------------
# Run Flask app
# -----------------------
if __name__ == "__main__":
    print(f"Bot is live at https://<your-render-app>.onrender.com/{BOT_TOKEN}")
    application.initialize()  # Ensure the Application is properly initialized
    app.run(host="0.0.0.0", port=PORT)
