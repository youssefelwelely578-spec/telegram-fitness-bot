import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

# Comprehensive Workout Database
WORKOUTS = {
    "chest": """
💪 **CHEST WORKOUT** (45-60 minutes)

**Compound Movements:**
- Bench Press: 4 sets x 6-10 reps
- Incline Dumbbell Press: 3 sets x 8-12 reps
- Decline Bench Press: 3 sets x 8-12 reps

**Isolation & Pump:**
- Chest Flyes: 3 sets x 12-15 reps
- Cable Crossovers: 3 sets x 12-15 reps
- Push-ups: 3 sets to failure

**💡 Pro Tips:** 
- Keep shoulders back, chest up
- Squeeze at the top of each rep
- 2-3 minutes rest between heavy sets
""",

    "back": """
💪 **BACK WORKOUT** (45-60 minutes)

**Vertical Pulling:**
- Pull-ups/Chin-ups: 4 sets x 6-12 reps
- Lat Pulldowns: 3 sets x 10-12 reps

**Horizontal Pulling:**
- Bent-over Rows: 4 sets x 8-10 reps
- Seated Cable Rows: 3 sets x 10-12 reps

**Rear Delts & Traps:**
- Face Pulls: 3 sets x 15-20 reps
- Shrugs: 3 sets x 12-15 reps

**💡 Pro Tips:** 
- Squeeze shoulder blades together
- Keep back straight, don't use momentum
""",

    "biceps": """
💪 **BICEPS WORKOUT** (30 minutes)

**Main Movements:**
- Barbell Curls: 4 sets x 8-12 reps
- Dumbbell Curls: 3 sets x 10-12 reps

**Isolation & Peak:**
- Hammer Curls: 3 sets x 10-12 reps
- Concentration Curls: 3 sets x 12-15 reps
- Preacher Curls: 3 sets x 10-12 reps

**💡 Pro Tips:** 
- Control the negative (lowering phase)
- Don't swing your body
- Squeeze at the top
""",

    "triceps": """
💪 **TRICEPS WORKOUT** (30 minutes)

**Compound Movements:**
- Close Grip Bench Press: 4 sets x 8-10 reps
- Dips: 3 sets x 10-15 reps

**Isolation:**
- Tricep Pushdowns: 3 sets x 12-15 reps
- Overhead Tricep Extension: 3 sets x 10-12 reps
- Skull Crushers: 3 sets x 10-12 reps

**💡 Pro Tips:** 
- Keep elbows tucked in
- Full range of motion
""",

    "shoulders": """
💪 **SHOULDERS WORKOUT** (45 minutes)

**Main Press:**
- Overhead Press: 4 sets x 6-10 reps
- Arnold Press: 3 sets x 10-12 reps

**Side Delts:**
- Lateral Raises: 4 sets x 12-15 reps
- Upright Rows: 3 sets x 10-12 reps

**Rear Delts:**
- Rear Delt Flyes: 3 sets x 15-20 reps
- Face Pulls: 3 sets x 15-20 reps

**💡 Pro Tips:** 
- Don't use too much weight on raises
- Focus on perfect form
""",

    "legs": """
🦵 **LEGS WORKOUT** (60 minutes)

**Quad Focus:**
- Barbell Squats: 4 sets x 6-10 reps
- Leg Press: 3 sets x 10-15 reps
- Lunges: 3 sets x 10-12 reps per leg

**Hamstrings:**
- Deadlifts: 3 sets x 6-8 reps
- Leg Curls: 3 sets x 12-15 reps

**Calves:**
- Calf Raises: 4 sets x 15-20 reps

**💡 Pro Tips:** 
- Warm up properly
- Don't skip leg day!
- Progressive overload is key
"""
}

# Nutrition Information
NUTRITION = {
    "general": """
🥗 **GENERAL NUTRITION GUIDELINES**

**Macronutrients:**
- Protein: 1.6-2.2g per kg bodyweight
- Carbs: 3-5g per kg bodyweight
- Fats: 0.8-1g per kg bodyweight

**Meal Timing:**
- Eat every 3-4 hours
- Protein with every meal
- Carbs around workouts
- Stay hydrated (3-4L daily)

**Food Quality:**
- Whole foods over processed
- Colorful vegetables
- Lean protein sources
- Healthy fats
""",

    "weight_loss": """
📉 **WEIGHT LOSS NUTRITION**

**Calorie Deficit:** 300-500 below maintenance
**Protein:** 2-2.5g per kg bodyweight
**Carbs:** 2-3g per kg bodyweight

**Sample Day:**
- Breakfast: Eggs + vegetables
- Lunch: Chicken salad + avocado
- Dinner: Fish + vegetables + quinoa
- Snacks: Greek yogurt, fruits, nuts

**Key Principles:** Calorie deficit, high protein, fiber, hydration
""",

    "muscle_gain": """
💪 **MUSCLE GAIN NUTRITION**

**Calorie Surplus:** 300-500 above maintenance
**Protein:** 1.8-2.2g per kg bodyweight
**Carbs:** 4-6g per kg bodyweight

**Sample Day:**
- Breakfast: Oatmeal + protein + fruits
- Pre-workout: Carbs + protein
- Post-workout: Fast protein + carbs
- Dinner: Meat + carbs + vegetables

**Key Principles:** Calorie surplus, protein timing, progressive overload
"""
}

# Exercise Form Tips
EXERCISE_TIPS = {
    "squat": "🦵 **SQUAT FORM:** Feet shoulder-width, chest up, break at hips/knees together, depth to parallel, drive through heels",
    "deadlift": "🏋️ **DEADLIFT FORM:** Bar over mid-foot, flat back, grip bar, drive through feet, keep bar close to body",
    "bench": "🏋️ **BENCH FORM:** Arch slightly, shoulder blades back, bar to lower chest, elbows at 45°, press explosively",
    "pullup": "💪 **PULL-UP FORM:** Grip wider than shoulders, pull chest to bar, control descent, full range of motion"
}

# Store user data for personalized plans
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🤖 **FITCOACH AI** - Your Complete Gym Coach\n\n"
        "💪 **Workouts:** chest, back, biceps, triceps, shoulders, legs\n"
        "🥗 **Nutrition:** general, weight loss, muscle gain\n"
        "🎯 **Personalized Diet Plan:** Type 'diet plan'\n"
        "🏋️ **Exercise Tips:** squat, deadlift, bench, pullup\n\n"
        "Ask me anything fitness-related!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text.lower()
    user_id = update.message.from_user.id
    
    # Store user message for context
    if user_id not in user_data:
        user_data[user_id] = {"conversation": []}
    user_data[user_id]["conversation"].append(user_message)
    
    # Workout responses
    if any(word in user_message for word in ['chest', 'bench', 'push']):
        await update.message.reply_text(WORKOUTS["chest"])
    
    elif any(word in user_message for word in ['back', 'pull', 'row']):
        await update.message.reply_text(WORKOUTS["back"])
    
    elif any(word in user_message for word in ['bicep', 'curl']):
        await update.message.reply_text(WORKOUTS["biceps"])
    
    elif any(word in user_message for word in ['tricep', 'pushdown', 'extension']):
        await update.message.reply_text(WORKOUTS["triceps"])
    
    elif any(word in user_message for word in ['shoulder', 'delt', 'press']):
        await update.message.reply_text(WORKOUTS["shoulders"])
    
    elif any(word in user_message for word in ['leg', 'squat', 'deadlift']):
        await update.message.reply_text(WORKOUTS["legs"])
    
    # Nutrition responses
    elif 'weight loss' in user_message or 'lose fat' in user_message:
        await update.message.reply_text(NUTRITION["weight_loss"])
    
    elif 'muscle gain' in user_message or 'bulk' in user_message:
        await update.message.reply_text(NUTRITION["muscle_gain"])
    
    elif 'nutrition' in user_message or 'diet' in user_message:
        await update.message.reply_text(NUTRITION["general"])
    
    # Personalized diet plan
    elif 'diet plan' in user_message or 'personalized' in user_message:
        await update.message.reply_text(
            "🥗 **PERSONALIZED DIET PLAN CREATOR**\n\n"
            "To create your custom diet plan, I need:\n"
            "1. Your age\n"
            "2. Weight (kg)\n"  
            "3. Height (cm)\n"
            "4. Activity level (sedentary/light/moderate/active/very active)\n"
            "5. Goal (weight loss/muscle gain/maintenance)\n\n"
            "Example: \"I'm 25 years old, 75kg, 180cm, moderate activity, want muscle gain\"\n\n"
            "Or answer step by step - just type your age first!"
        )
        user_data[user_id]["waiting_for_diet_info"] = True
    
    # Exercise form tips
    elif 'squat' in user_message and 'form' in user_message:
        await update.message.reply_text(EXERCISE_TIPS["squat"])
    elif 'deadlift' in user_message and 'form' in user_message:
        await update.message.reply_text(EXERCISE_TIPS["deadlift"])
    elif 'bench' in user_message and 'form' in user_message:
        await update.message.reply_text(EXERCISE_TIPS["bench"])
    elif 'pull' in user_message and 'form' in user_message:
        await update.message.reply_text(EXERCISE_TIPS["pullup"])
    
    # General fitness questions
    elif any(word in user_message for word in ['how many', 'how much', 'how to']):
        responses = [
            "💡 Focus on progressive overload - increase weight/reps each week!",
            "🎯 Consistency is key - 3-4 workouts per week minimum!",
            "🥗 Nutrition is 70% of results - track your calories!",
            "💪 Form over weight - perfect your technique first!",
            "🛌 Recovery is crucial - aim for 7-8 hours sleep!"
        ]
        import random
        await update.message.reply_text(random.choice(responses))
    
    # Greetings
    elif any(word in user_message for word in ['hi', 'hello', 'hey']):
        await update.message.reply_text("👋 Hello! I'm your AI gym coach. Ask me about workouts, nutrition, or exercise tips!")
    
    # Thank you
    elif any(word in user_message for word in ['thank', 'thanks']):
        await update.message.reply_text("You're welcome! 💪 Keep crushing your fitness goals!")
    
    # Default response
    else:
        await update.message.reply_text(
            "🤖 **Quick Commands:**\n"
            "• Chest/Back/Arms/Shoulders/Legs workout\n"  
            "• Weight loss/Muscle gain nutrition\n"
            "• Diet plan (personalized)\n"
            "• Exercise form tips\n\n"
            "What would you like to know?"
        )

# Health server (keep Render happy)
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        return

def run_health_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

def main():
    # Start health server
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # Create bot application
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start bot with auto-restart
    import time
    while True:
        try:
            logger.info("🤖 FitCoach AI starting...")
            application.run_polling(drop_pending_updates=True)
        except Exception as e:
            logger.error(f"Error: {e}. Restarting in 5 seconds...")
            time.sleep(5)

if __name__ == '__main__':
    main()
