import os
import asyncio
from flask import Flask, request
import openai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)

# ------------------------------
# Load environment variables
# ------------------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
PORT = int(os.environ.get("PORT", 5000))

# ------------------------------
# Flask server for Render
# ------------------------------
server = Flask(__name__)

@server.route("/")
def home():
    return "Telegram AI Personal Trainer is running!"

@server.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        if not data:
            return "no data"

        update = Update.de_json(data, bot_app.bot)
        asyncio.get_event_loop().create_task(bot_app.process_update(update))
    except Exception as e:
        print("Webhook error:", e, flush=True)
    return "ok"

# ------------------------------
# OpenAI helper
# ------------------------------
async def get_ai_text(prompt):
    try:
        response = await asyncio.to_thread(lambda: openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful personal trainer."},
                {"role": "user", "content": prompt}
            ]
        ))
        return response.choices[0].message.content
    except Exception as e:
        print("OpenAI Error:", e)
        return "Sorry, I can't generate a response right now."

# ------------------------------
# Bot commands
# ------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I'm your AI personal trainer 🤖💪\n"
        "Ask me any fitness question, or type /nutrition for a personalized nutrition plan."
    )

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    user_input = update.message.text
    text = await get_ai_text(f"A client asks: {user_input}")
    await update.message.reply_text(text)

# ------------------------------
# Nutrition conversation
# ------------------------------
NUT_AGE, NUT_HEIGHT, NUT_WEIGHT, NUT_ACTIVITY, NUT_GOAL = range(5)

async def nutrition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Let's create your personalized nutrition plan! How old are you?")
    return NUT_AGE

async def nut_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['nut_age'] = update.message.text
    await update.message.reply_text("What is your height in cm?")
    return NUT_HEIGHT

async def nut_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['nut_height'] = update.message.text
    await update.message.reply_text("What is your weight in kg?")
    return NUT_WEIGHT

async def nut_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['nut_weight'] = update.message.text
    await update.message.reply_text("Describe your activity level (sedentary, moderate, active):")
    return NUT_ACTIVITY

async def nut_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['nut_activity'] = update.message.text
    await update.message.reply_text("What is your goal? (lose weight, maintain, gain muscle)")
    return NUT_GOAL

async def nut_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['nut_goal'] = update.message.text
    prompt = (
        f"Create a personalized nutrition plan for a person with:\n"
        f"Age: {context.user_data['nut_age']}, "
        f"Height: {context.user_data['nut_height']} cm, "
        f"Weight: {context.user_data['nut_weight']} kg, "
        f"Activity: {context.user_data['nut_activity']}, "
        f"Goal: {context.user_data['nut_goal']}.\n"
        f"Include meals, portion sizes, and healthy tips."
    )
    text = await get_ai_text(prompt)
    await update.message.reply_text(text)
    return ConversationHandler.END

nutrition_conv = ConversationHandler(
    entry_points=[CommandHandler('nutrition', nutrition)],
    states={
        NUT_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, nut_age)],
        NUT_HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, nut_height)],
        NUT_WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, nut_weight)],
        NUT_ACTIVITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, nut_activity)],
        NUT_GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, nut_goal)],
    },
    fallbacks=[]
)

# ------------------------------
# Initialize bot
# ------------------------------
bot_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(nutrition_conv)
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_question))

# ------------------------------
# Run Flask + Telegram webhook
# ------------------------------
if __name__ == "__main__":
    bot_app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"https://telegram-fitness-bot-1.onrender.com/{TELEGRAM_TOKEN}"
    )
