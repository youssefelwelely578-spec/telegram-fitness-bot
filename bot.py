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
""",
        "weight_loss": """
🔥 **Beginner Weight Loss Circuit**

**Circuit (repeat 3x):**
- Jumping Jacks: 1 minute
- Bodyweight Squats: 15 reps
- Push-ups: 10 reps
- Mountain Climbers: 30 seconds
- Rest: 1 minute between circuits
"""
    },
    "intermediate": {
        "push_pull_legs": """
💪 **Intermediate PPL Routine**

**Push Day (Chest/Shoulders/Triceps):**
- Bench Press: 4x8
- Overhead Press: 4x8
- Incline Press: 3x10
- Tricep Extensions: 3x12

**Pull Day (Back/Biceps):**
- Pull-ups: 4x8
- Rows: 4x8
- Face Pulls: 3x15
- Bicep Curls: 3x12

**Leg Day:**
- Squats: 4x8
- Deadlifts: 4x5
- Leg Press: 3x10
- Calf Raises: 4x15
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
5. **Whole foods**: Prioritize unprocessed foods
""",
    "weight_loss": """
📉 **Weight Loss Nutrition:**

- **Calorie deficit**: 300-500 below maintenance
- **High protein**: Preserve muscle mass
- **Fiber-rich foods**: Keep you full
- **Avoid sugary drinks**
- **Meal timing**: Consistent eating schedule
""",
    "muscle_gain": """
💪 **Muscle Gain Nutrition:**

- **Calorie surplus**: 300-500 above maintenance
- **Protein timing**: Post-workout window
- **Carb cycling**: More carbs on workout days
- **Healthy fats**: For hormone production
"""
}

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = """
🤖 **Welcome to Your Personal Fitness AI Trainer!**

I'm here to help you with all things fitness and nutrition. Here's what I can do:

**🏋️ Workout Plans:**
- /beginner - Beginner workout plans
- /intermediate - Intermediate routines
- /custom - Create custom workout

**🥗 Nutrition:**
- /nutrition - General nutrition tips
- /dietplan - Create personalized diet plan
- /weightloss - Weight loss nutrition
- /musclegain - Muscle building nutrition

**💪 Quick Commands:**
- /backworkout - Back exercises
- /chestworkout - Chest exercises
- /legworkout - Leg exercises
- /cardio - Cardio routines

**💡 Just ask me anything about fitness, workouts, or nutrition!**
"""
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all text messages"""
    user_message = update.message.text.lower()
    
    # Workout-related questions
    if any(word in user_message for word in ['workout', 'exercise', 'train', 'gym', 'lift']):
        if 'back' in user_message:
            response = """
💪 **Back Workout Essentials:**

**Compound Movements:**
- Pull-ups/Chin-ups: 3-4 sets of 6-12 reps
- Bent-over Barbell Rows: 3-4 sets of 8-12 reps
- Deadlifts: 3-4 sets of 5-8 reps

**Accessory Work:**
- Lat Pulldowns: 3 sets of 10-15 reps
- Seated Cable Rows: 3 sets of 10-12 reps
- Face Pulls: 3 sets of 15-20 reps

**Focus on mind-muscle connection and full range of motion!**
"""
        elif 'chest' in user_message:
            response = """
🏋️ **Chest Development:**

**Main Exercises:**
- Bench Press: 3-4 sets of 6-12 reps
- Incline Dumbbell Press: 3 sets of 8-12 reps
- Decline Press: 3 sets of 8-12 reps

**Isolation:**
- Chest Flyes: 3 sets of 12-15 reps
- Cable Crossovers: 3 sets of 12-15 reps
- Push-ups: 3 sets to failure

**Keep shoulders back and chest up!**
"""
        elif 'leg' in user_message or 'squat' in user_message:
            response = """
🦵 **Leg Day Protocol:**

**Quad Focus:**
- Squats: 4 sets of 6-10 reps
- Leg Press: 3 sets of 10-15 reps
- Lunges: 3 sets of 10-12 reps per leg

**Hamstrings/Glutes:**
- Deadlifts: 3 sets of 6-8 reps
- Romanian Deadlifts: 3 sets of 10-12 reps
- Hip Thrusts: 3 sets of 12-15 reps

**Don't skip leg day!**
"""
        else:
            response = "💪 Tell me more about what you want to work on! Specific muscle group? Goals?"
    
    # Nutrition questions
    elif any(word in user_message for word in ['diet', 'nutrition', 'eat', 'food', 'calorie']):
        if 'weight loss' in user_message or 'lose weight' in user_message:
            response = NUTRITION_TIPS['weight_loss']
        elif 'muscle' in user_message or 'gain' in user_message:
            response = NUTRITION_TIPS['muscle_gain']
        else:
            response = NUTRITION_TIPS['general']
    
    # General fitness questions
    elif any(word in user_message for word in ['how to', 'what is', 'should i', 'can i']):
        responses = [
            "Focus on progressive overload and consistency!",
            "Make sure you're getting enough protein and sleep!",
            "Form is more important than weight - prioritize technique!",
            "Consistency beats intensity every time!",
            "Remember to warm up properly and stretch after workouts!"
        ]
        response = random.choice(responses)
    
    else:
        response = """
🤔 I'm your fitness AI! Ask me about:
- Specific workout routines
- Nutrition advice
- Exercise techniques
- Fitness goals
- Or use /help for command list
"""
    
    await update.message.reply_text(response)

async def create_diet_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Create personalized diet plan based on user info"""
    await update.message.reply_text(
        "🥗 **Personalized Diet Plan Creator**\n\n"
        "To create your custom diet plan, I'll need:\n"
        "1. Your age\n"
        "2. Weight (kg)\n"
        "3. Height (cm)\n"
        "4. Activity level (sedentary/light/moderate/active)\n"
        "5. Goal (weight loss/muscle gain/maintenance)\n\n"
        "Example: \"I'm 25, 75kg, 180cm, moderate activity, want muscle gain\""
    )

async def beginner_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(WORKOUT_PLANS['beginner']['full_body'])

async def nutrition_tips(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(NUTRITION_TIPS['general'])

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = """
📋 **Available Commands:**

**Workouts:**
/beginner - Beginner workout plans
/intermediate - Intermediate routines
/backworkout - Back exercises
/chestworkout - Chest exercises
/legworkout - Leg exercises

**Nutrition:**
/nutrition - General nutrition tips
/dietplan - Create personalized diet
/weightloss - Weight loss nutrition
/musclegain - Muscle building nutrition

**Just type your fitness questions!** I understand natural language.
"""
    await update.message.reply_text(help_text)

def main() -> None:
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("beginner", beginner_plan))
    application.add_handler(CommandHandler("nutrition", nutrition_tips))
    application.add_handler(CommandHandler("dietplan", create_diet_plan))
    
    # Add message handler for all text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    print("🤖 Fitness AI Trainer is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
