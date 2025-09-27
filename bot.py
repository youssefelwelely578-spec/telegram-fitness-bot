import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
Application, CommandHandler, MessageHandler,
ConversationHandler, ContextTypes, filters
)
import openai

# ------------------------------

# ENV VARIABLES

# ------------------------------

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# ------------------------------

# FLASK SERVER

# ------------------------------

PORT = int(os.environ.get("PORT", 5000))
server = Flask(**name**)

# ------------------------------

# TELEGRAM APP

# ------------------------------

app = Application.builder().token(TELEGRAM_TOKEN).build()

# --- Nutrition states ---

NUT_AGE, NUT_HEIGHT, NUT_WEIGHT, NUT_ACTIVITY, NUT_GOAL = range(5)

# ------------------------------

# OpenAI Helpers

# ------------------------------

async def get_ai_text(prompt: str):
try:
response = await asyncio.to_thread(lambda: openai.ChatCompletion.create(
model="gpt-4",
messages=[
{"role": "system", "content": "You are a helpful personal trainer."},
{"role": "user", "content": prompt}
]
))
return response.choices[0].message.content
except Exception as e:
print("OpenAI Error:", e)
return "⚠️ Error: could not generate response."

# ------------------------------

# Bot Handlers

# ------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
"Hi! I'm your AI personal trainer 🤖💪\n"
"Ask me anything about fitness or type /nutrition for a custom meal plan."
)

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
user_input = update.message.text
reply = await get_ai_text(user_input)
await update.message.reply_text(reply)

async def nutrition(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text("Let's make a nutrition plan! How old are you?")
return NUT_AGE

async def nut_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
context.user_data["nut_age"] = update.message.text
await update.message.reply_text("Your height in cm?")
return NUT_HEIGHT

async def nut_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
context.user_data["nut_height"] = update.message.text
await update.message.reply_text("Your weight in kg?")
return NUT_WEIGHT

async def nut_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
context.user_data["nut_weight"] = update.message.text
await update.message.reply_text("Activity level (sedentary, moderate, active)?")
return NUT_ACTIVITY

async def nut_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
context.user_data["nut_activity"] = update.message.text
await update.message.reply_text("Goal? (lose weight, maintain, gain muscle)")
return NUT_GOAL

async def nut_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
context.user_data["nut_goal"] = update.message.text
prompt = (
f"Make a nutrition plan:\n"
f"Age: {context.user_data['nut_age']}, "
f"Height: {context.user_data['nut_height']} cm, "
f"Weight: {context.user_data['nut_weight']} kg, "
f"Activity: {context.user_data['nut_activity']}, "
f"Goal: {context.user_data['nut_goal']}."
)
reply = await get_ai_text(prompt)
await update.message.reply_text(reply)
return ConversationHandler.END

nutrition_conv = ConversationHandler(
entry_points=[CommandHandler("nutrition", nutrition)],
states={
NUT_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, nut_age)],
NUT_HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, nut_height)],
NUT_WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, nut_weight)],
NUT_ACTIVITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, nut_activity)],
NUT_GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, nut_goal)],
},
fallbacks=[]
)

# Register handlers

app.add_handler(CommandHandler("start", start))
app.add_handler(nutrition_conv)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_question))

# ------------------------------

# Webhook route

# ------------------------------

@server.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
try:
data = request.get_json(force=True)
update = Update.de_json(data, app.bot)
asyncio.get_event_loop().create_task(app.process_update(update))
except Exception as e:
print("Webhook error:", e)
return "ok"

@server.route("/")
def home():
return "🤖 Telegram Fitness Bot is running!"

# ------------------------------

# Start Webhook (when app launches)

# ------------------------------

async def set_webhook():
await app.bot.set_webhook(
url=f"[https://telegram-fitness-bot-1.onrender.com/{TELEGRAM_TOKEN}](https://telegram-fitness-bot-1.onrender.com/{TELEGRAM_TOKEN})"
)

if **name** == "**main**":
asyncio.get_event_loop().run_until_complete(set_webhook())
server.run(host="0.0.0.0", port=PORT)
