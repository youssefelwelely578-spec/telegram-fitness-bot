import os
import logging
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Quick direct responses
KNOWLEDGE = {
    "water": "💧 3-4 liters daily. More if active.",
    "post_workout": "🥗 Protein + carbs within 1-2h. Chicken + rice or protein shake.",
    "protein": "💪 1.6-2.2g per kg bodyweight daily.",
    "sleep": "😴 7-9 hours for recovery.",
    
    "chest": "Bench 4x8, Incline 3x10, Flyes 3x12",
    "back": "Pull-ups 4x8, Rows 4x10, Pulldowns 3x12", 
    "biceps": "Curls 4x10, Hammer 3x12, Concentration 3x15",
    "triceps": "Pushdowns 4x12, Dips 3x15, Extensions 3x10",
    "shoulders": "OHP 4x8, Lateral 3x15, Front 3x12",
    "legs": "Squats 4x8, Deadlifts 3x6, Lunges 3x10",
    
    "weight_loss": "Calorie deficit, high protein, limit processed foods",
    "muscle_gain": "Calorie surplus, protein 2g/kg, progressive overload"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 FitCoach - Ask me anything fitness related")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.lower()
    
    if any(word in user_message for word in ['water', 'drink', 'hydrate']):
        await update.message.reply_text(KNOWLEDGE["water"])
    
    elif any(word in user_message for word in ['after gym', 'after workout', 'post workout']):
        await update.message.reply_text(KNOWLEDGE["post_workout"])
    
    elif 'protein' in user_message:
        await update.message.reply_text(KNOWLEDGE["protein"])
    
    elif 'sleep' in user_message:
        await update.message.reply_text(KNOWLEDGE["sleep"])
    
    elif 'chest' in user_message:
        await update.message.reply_text("💪 " + KNOWLEDGE["chest"])
    elif 'back' in user_message:
        await update.message.reply_text("💪 " + KNOWLEDGE["back"])
    elif 'bicep' in user_message:
        await update.message.reply_text("💪 " + KNOWLEDGE["biceps"])
    elif 'tricep' in user_message:
        await update.message.reply_text("💪 " + KNOWLEDGE["triceps"])
    elif 'shoulder' in user_message:
        await update.message.reply_text("💪 " + KNOWLEDGE["shoulders"])
    elif 'leg' in user_message:
        await update.message.reply_text("🦵 " + KNOWLEDGE["legs"])
    
    elif 'weight loss' in user_message:
        await update.message.reply_text(KNOWLEDGE["weight_loss"])
    elif 'muscle gain' in user_message:
        await update.message.reply_text(KNOWLEDGE["muscle_gain"])
    
    elif 'hi' in user_message or 'hello' in user_message:
        await update.message.reply_text("👋 Ask me about workouts or nutrition")
    
    else:
        await update.message.reply_text("💪 Ask: water, protein, chest/back/legs workout, etc.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    while True:
        try:
            application.run_polling(drop_pending_updates=True)
        except Exception as e:
            time.sleep(10)
            continue

if __name__ == '__main__':
    main()
