import os
import logging
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

# Fitness knowledge database
WORKOUT_PLANS = {
    "beginner": {
        "full_body": """
🏋️ **Beginner Full Body Workout (3 days/week)**

**Day 1:**
- Squats: 3x10
- Push-ups: 3x10
- Bent-over Rows: 3x10
- Plank: 3x30 seconds

**Day 2:**
- Lunges: 3x10 per leg
- Dumbbell Press: 3x10
- Lat Pulldowns: 3x10
- Leg Raises: 3x15

**Day 3:**
- Deadlifts: 3x8
- Shoulder Press: 3x10
- Bicep Curls: 3x12
- Russian Twists: 3x15
"""
    }
}

NUTRITION_TIPS = {
    "general": """
🥗 **General Nutrition Principles:**

1. **Protein**: 1.6-2.2g per kg bodyweight
2. **Carbs**: Fuel your workouts
3. **Fats**: Essential for hormones
4. **Hydration**: 3-4 liters daily
"""
}

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = """
🤖 **Welcome to Your Personal Fitness AI Trainer!**

**Commands:**
/start - Show this message
/beginner - Beginner workout plans  
/nutrition - Nutrition tips
/help - All commands

💡 **Just ask me anything about fitness!**
"""
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all text messages"""
    user_message = update.message.text.lower()
    
    if any(word in user_message for word in ['workout', 'exercise', 'gym']):
        if 'back' in user_message:
            response = "💪 **Back Exercises:** Pull-ups, Rows, Deadlifts\n3-4 sets of 8-12 reps"
        elif 'chest' in user_message:
            response = "🏋️ **Chest Exercises:** Bench Press, Push-ups, Flyes\n3-4 sets of 8-12 reps"
        elif 'leg' in user_message:
            response = "🦵 **Leg Exercises:** Squats, Lunges, Deadlifts\n3-4 sets of 8-12 reps"
        else:
            response = "💪 Tell me which muscle group you want to work on!"
    
    elif any(word in user_message for word in ['diet', 'nutrition', 'food']):
        response = NUTRITION_TIPS['general']
    
    else:
        response = "🤖 Ask me about workouts, nutrition, or fitness tips!"
    
    await update.message.reply_text(response)

async def beginner_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(WORKOUT_PLANS['beginner']['full_body'])

async def nutrition_tips(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(NUTRITION_TIPS['general'])

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = """
📋 **Available Commands:**
/start - Welcome message
/beginner - Beginner workout
/nutrition - Nutrition tips

💡 **Just type your fitness questions!**
"""
    await update.message.reply_text(help_text)

def main() -> None:
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("beginner", beginner_plan))
    application.add_handler(CommandHandler("nutrition", nutrition_tips))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot with error handling
    try:
        print("🤖 Starting Fitness AI Trainer...")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True  # This clears any pending updates from other instances
        )
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        # Wait and restart
        import time
        time.sleep(10)
        main()  # Restart

if __name__ == '__main__':
    main()
