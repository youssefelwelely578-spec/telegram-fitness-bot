# bot.py
import os
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
# Load API keys from Render environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")
# AI text response
def get_ai_text(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful personal trainer."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
# AI image generation (DALL·E)
def get_ai_image(prompt):
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="512x512"
    )
    return response['data'][0]['url']
# Telegram command handlers
async def workout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = get_ai_text("Create a beginner-friendly workout plan.")
    await update.message.reply_text(text)
async def workout_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    image_url = get_ai_image("Beginner workout exercises illustration")
    await update.message.reply_photo(photo=image_url)
async def nutrition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = get_ai_text("Create a beginner-friendly nutrition plan.")
    await update.message.reply_text(text)
async def nutrition_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    image_url = get_ai_image("Healthy meal plan illustration")
    await update.message.reply_photo(photo=image_url)
# Initialize bot
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("workout", workout))
app.add_handler(CommandHandler("workout_photo", workout_photo))
app.add_handler(CommandHandler("nutrition", nutrition))
app.add_handler(CommandHandler("nutrition_photo", nutrition_photo))
# Run bot
app.run_polling()
