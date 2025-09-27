import os
import openai
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
from flask import Flask

# --- Environment variables ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.environ.get("PORT", 5000))

openai.api_key = OPENAI_API_KEY

# --- Conversation states ---
AGE, HEIGHT, WEIGHT, ACTIVITY = range(4)
NUT_AGE, NUT_HEIGHT, NUT_WEIGHT, NUT_ACTIVITY, NUT_GOAL = range(5, 10)

# --- Flask server for Render health check ---
server = Flask(__name__)

@server.route("/")
def home():
    return "Bot is live!"

# --- Async OpenAI helpers ---
async def get_ai_text(prompt):
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
        return "Sorry, I can't generate a response right now."

async def get_ai_image(prompt):
    try:
        response = await asyncio.to_thread(lambda: openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        ))
        return response['data'][0]['url']
    except Exception as e:
        print("OpenAI Image Error:", e)
        return None

# --- /start command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I’m your personal AI trainer 🤖💪\n"
        "Use /workout for workout plans, /nutrition for nutrition advice, "
        "or just ask a fitness question!"
    )

# --- General Q&A ---
async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    answer = await get_ai_text(f"A client asks: {question}")
    await update.message.reply_text(answer)

# --- Workout conversation ---
async def workout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Let's make a personalized workout plan! How old are you?")
    return AGE

async def age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['age'] = update.message.text
    await update.message.reply_text("What is your height in cm?")
    return HEIGHT

async def height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['height'] = update.message.text
    await update.message.reply_text("What is your weight in kg?")
    return WEIGHT

async def weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['weight'] = update.message.text
    await update.message.reply_text("Describe your activity level (sedentary, moderate, active):")
    return ACTIVITY

async def activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['activity'] = update.message.text
    prompt = (
        f"Create a personalized beginner workout plan for a person with:\n"
        f"Age: {context.user_data['age']}, Height: {context.user_data['height']} cm, "
        f"Weight: {context.user_data['weight']} kg, Activity: {context.user_data['activity']}.\n"
        f"Include step-by-step instructions and exercise illustrations."
    )
    text = await get_ai_text(prompt)
    image_url = await get_ai_image("Illustration for beginner workout exercises")
    await update.message.reply_text(text)
    if image_url:
        await update.message.reply_photo(photo=image_url)
    return ConversationHandler.END

workout_conv = ConversationHandler(
    entry_points=[CommandHandler('workout', workout)],
    states={
        AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
        HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, height)],
        WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, weight)],
        ACTIVITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, activity)],
    },
    fallbacks=[]
)

# --- Nutrition conversation ---
async def nutrition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Let's create a personalized nutrition plan! How old are you?")
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
        f"Age: {context.user_data['nut_age']}, Height: {context.user_data['nut_height']} cm, "
        f"Weight: {context.user_data['nut_weight']} kg, Activity: {context.user_data['nut_activity']}, "
        f"Goal: {context.user_data['nut_goal']}.\n"
        f"Include meals, portion sizes, and healthy tips."
    )
    text = await get_ai_text(prompt)
    image_url = await get_ai_image("Healthy meal plan illustration")
    await update.message.reply_text(text)
    if image_url:
        await update.message.reply_photo(photo=image_url)
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

# --- Error handler ---
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"Exception: {context.error}")
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("Oops! Something went wrong. Try again later.")

# --- Initialize bot ---
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(workout_conv)
app.add_handler(nutrition_conv)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_question))
app.add_error_handler(error_handler)

# --- Run webhook (Render Web Service) ---
app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path=TELEGRAM_TOKEN,
    webhook_url=f"https://telegram-fitness-bot-1.onrender.com/{TELEGRAM_TOKEN}"
)
