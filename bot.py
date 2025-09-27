import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Bot configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN")
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "telegram-fitness-bot-1.onrender.com")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set!")

# Create application
application = Application.builder().token(BOT_TOKEN).build()

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🤖 **Fitness AI Trainer Ready!** Ask me about workouts or nutrition!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text.lower()
    
    if 'workout' in user_message or 'exercise' in user_message:
        if 'back' in user_message:
            response = "💪 **Back Day:**\n- Pull-ups: 3x8\n- Rows: 3x10\n- Deadlifts: 3x5"
        elif 'chest' in user_message:
            response = "🏋️ **Chest Day:**\n- Bench Press: 3x8\n- Push-ups: 3x12\n- Flyes: 3x12"
        elif 'leg' in user_message:
            response = "🦵 **Leg Day:**\n- Squats: 3x8\n- Lunges: 3x10\n- Calf Raises: 3x15"
        else:
            response = "💪 **Full Body:**\n- Squats: 3x10\n- Push-ups: 3x10\n- Rows: 3x10"
    
    elif 'nutrition' in user_message or 'diet' in user_message:
        response = "🥗 **Nutrition Tips:**\n- Protein: 1.6g/kg\n- Carbs for energy\n- Healthy fats\n- Stay hydrated!"
    
    else:
        response = "🤖 Ask me about:\n- Workout plans\n- Nutrition advice\n- Exercise techniques"
    
    await update.message.reply_text(response)

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Webhook route
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.get_json(), application.bot)
        asyncio.run(application.process_update(update))
        return 'ok'
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return 'error'

@app.route('/')
def home():
    return "Fitness Bot is running!"

@app.route('/set_webhook')
def set_webhook():
    try:
        # FIXED: Remove duplicate https://
        webhook_url = f"https://{RENDER_EXTERNAL_URL}/webhook"
        # FIXED: Add await
        result = asyncio.run(application.bot.set_webhook(webhook_url))
        return f"Webhook set: {result}"
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    # Set webhook on startup - FIXED with proper async handling
    try:
        webhook_url = f"https://{RENDER_EXTERNAL_URL}/webhook"  # FIXED URL
        result = asyncio.run(application.bot.set_webhook(webhook_url))
        logger.info(f"Webhook set: {result} to {webhook_url}")
    except Exception as e:
        logger.error(f"Webhook setup failed: {e}")
    
    # Start Flask
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
