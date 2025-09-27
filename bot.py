import os
import openai
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)

# --- Load tokens ---
TELEGRAM_TOKEN = os.getenv("8426717766:AAGeYeMKt4wetni8l85LyUx_PsdnTF5Ue5E")
OPENAI_API_KEY = os.getenv("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")
openai.api_key = OPENAI_API_KEY

# --- Nutrition states ---
NUT_AGE, NUT_HEIGHT, NUT_WEIGHT, NUT_ACTIVITY, NUT_GOAL = range(5)

# --- OpenAI Helpers ---
async def get_ai_text(prompt: str):
    try:
        response = await openai.Chat.completions.acreate(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful and motivating personal trainer AI."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        print("OpenAI Error:", e)
        return "⚠️ Sorry, I can't generate a response right now."

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I'm your AI Personal Trainer 🤖💪\n"
        "Ask me any fitness question, or type /nutrition for a custom meal plan."
    )

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    text = await get_ai_text(f"A client asks: {user_input}")
    await update.message.reply_text(text)

# --- Nutrition Conversation ---
async def nutrition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Let's create your nutrition plan! How old are you?")
    return NUT_AGE

async def nut_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['age'] = update.message.text
    await update.message.reply_text("What is your height in cm?")
    return NUT_HEIGHT

async def nut_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['height'] = update.message.text
    await update.message.reply_text("What is your weight in kg?")
    return NUT_WEIGHT

async def nut_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['weight'] = update.message.text
    await update.message.reply_text("Describe your activity level (sedentary, moderate, active):")
    return NUT_ACTIVITY

async def nut_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['activity'] = update.message.text
    await update.message.reply_text("What is your goal? (lose weight, maintain, gain muscle)")
    return NUT_GOAL

async def nut_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['goal'] = update.message.text
    prompt = (
        f"Create a nutrition plan for:\n"
        f"Age: {context.user_data['age']} | "
        f"Height: {context.user_data['height']} cm | "
        f"Weight: {context.user_data['weight']} kg | "
        f"Activity: {context.user_data['activity']} | "
        f"Goal: {context.user_data['goal']}.\n"
        f"Include meals, portions, and healthy tips."
    )
    text = await get_ai_text(prompt)
    await update.message.reply_text(text)
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

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"Error: {context.error}")
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("⚠️ Something went wrong, please try again later.")

# --- Build Application ---
def build_app() -> Application:
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(nutrition_conv)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_question))
    app.add_error_handler(error_handler)
    return app
