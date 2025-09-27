import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# ---------------------------
# CONFIG
# ---------------------------
TOKEN = os.environ.get("TELEGRAM_TOKEN")  # set in Render environment
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # set in Render environment
PORT = int(os.environ.get("PORT", 10000))  # default 10000

# ---------------------------
# LOGGING
# ---------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------------------------
# FLASK APP
# ---------------------------
app = Flask(__name__)

# ---------------------------
# TELEGRAM BOT SETUP
# ---------------------------
bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()
application.initialize()  # important to initialize once at startup

# ---------------------------
# OPENAI HELPER
# ---------------------------
import openai
openai.api_key = OPENAI_API_KEY

async def get_ai_text(prompt: str) -> str:
    logger.info(f"Sending prompt to OpenAI: {prompt}")
    try:
        response = openai.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.choices[0].message.content
        logger.info(f"OpenAI response: {text}")
        return text
    except Exception as e:
        logger.error(f"OpenAI Error: {e}")
        return "Sorry, I couldn't get a response from OpenAI."

# ---------------------------
# TELEGRAM HANDLERS
# ---------------------------
async def start(update: Update, context):
    await update.message.reply_text("Hello! Send me a message and I'll answer using GPT-5-mini.")

async def handle_message(update: Update, context):
    user_text = update.message.text
    reply = await get_ai_text(user_text)
    await update.message.reply_text(reply)

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

# ---------------------------
# FLASK WEBHOOK ROUTE
# ---------------------------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    # schedule async processing without blocking Flask
    asyncio.create_task(application.process_update(update))
    return "ok"

# ---------------------------
# HEALTH CHECK
# ---------------------------
@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"

# ---------------------------
# RUN APP
# ---------------------------
if __name__ == "__main__":
    logger.info(f"Starting Flask server on port {PORT}")
    app.run(host="0.0.0.0", port=PORT)
