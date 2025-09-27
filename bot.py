import os
import logging
import threading
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
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

# Quick workout database
WORKOUTS = {
    "chest": """
💪 **Chest Workout:**
- Bench Press: 4 sets x 8-12 reps
- Incline Dumbbell Press: 3 sets x 10-12 reps  
- Chest Flyes: 3 sets x 12-15 reps
- Push-ups: 3 sets to failure

**Tip:** Focus on mind-muscle connection, keep shoulders back.
""",
    
    "back": """
💪 **Back Workout:**
- Pull-ups: 4 sets x 6-12 reps
- Bent-over Rows: 4 sets x 8-12 reps
- Lat Pulldowns: 3 sets x 10-12 reps
- Face Pulls: 3 sets x 15-20 reps

**Tip:** Squeeze your back muscles at the top of each rep.
""",
    
    "legs": """
🦵 **Leg Workout:**
- Squats: 4 sets x 6-10 reps
- Deadlifts: 3 sets x 6-8 reps
- Lunges: 3 sets x 10-12 reps per leg
- Leg Press: 3 sets x 12-15 reps

**Tip:** Don't skip leg day! Warm up properly.
""",
    
    "shoulders": """
💪 **Shoulder Workout:**
- Overhead Press: 4 sets x 8-12 reps
- Lateral Raises: 3 sets x 12-15 reps
- Front Raises: 3 sets x 12-15 reps
- Rear Delt Flyes: 3 sets x 15-20 reps

**Tip:** Keep core tight, don't use momentum.
""",
    
    "arms": """
💪 **Arm Workout:**
- Bicep Curls: 3 sets x 10-15 reps
- Tricep Pushdowns: 3 sets x 10-15 reps
- Hammer Curls: 3 sets x 10-12 reps
- Skull Crushers: 3 sets x 10-12 reps

**Tip:** Control the weight, don't swing.
"""
}

NUTRITION = {
    "weight loss": "📉 **Weight Loss:** Calorie deficit (maintenance - 500), high protein (1.6g/kg), lots of vegetables, limit processed foods.",
    "muscle gain": "💪 **Muscle Gain:** Calorie surplus (+300), protein (1.8-2.2g/kg), carbs around workouts, healthy fats.",
    "maintenance": "⚖️ **Maintenance:** Balanced macros, protein (1.2-1.6g/kg), variety of whole foods, stay hydrated."
}

EXERCISE_TIPS = {
    "squat": "🦵 **Squat:** Feet shoulder-width, break at hips/knees, keep chest up, drive through heels.",
    "deadlift": "🏋️ **Deadlift:** Bar over mid-foot, flat back, drive through feet, keep bar close.",
    "bench": "🏋️ **Bench:** Arch slightly, bar to lower chest, elbows at 45°, press explosively.",
    "pullup": "💪 **Pull-up:** Grip slightly wider than shoulders, pull chest to bar, control descent."
}

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🤖 **FitCoach AI** - Your quick fitness assistant. Ask me anything about workouts or nutrition!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text.lower()
    response = ""
    
    # Quick workout responses
    if 'chest' in user_message:
        response = WORKOUTS["chest"]
    elif 'back' in user_message:
        response = WORKOUTS["back"]
    elif 'leg' in user_message:
        response = WORKOUTS["legs"]
    elif 'shoulder' in user_message:
        response = WORKOUTS["shoulders"]
    elif 'arm' in user_message:
        response = WORKOUTS["arms"]
    elif 'full body' in user_message or 'beginner' in user_message:
        response = "💪 **Full Body Workout:**\n- Squats: 3x10\n- Bench Press: 3x10\n- Rows: 3x10\n- Overhead Press: 3x10\n- Plank: 3x30s"
    
    # Nutrition responses
    elif 'weight loss' in user_message or 'lose fat' in user_message:
        response = NUTRITION["weight loss"]
    elif 'muscle gain' in user_message or 'bulk' in user_message:
        response = NUTRITION["muscle gain"]
    elif 'diet' in user_message or 'nutrition' in user_message:
        response = "🥗 **Quick Nutrition:** " + random.choice(list(NUTRITION.values()))
    
    # Exercise tips
    elif 'squat' in user_message:
        response = EXERCISE_TIPS["squat"]
    elif 'deadlift' in user_message:
        response = EXERCISE_TIPS["deadlift"]
    elif 'bench' in user_message:
        response = EXERCISE_TIPS["bench"]
    elif 'pull' in user_message:
        response = EXERCISE_TIPS["pullup"]
    
    # Quick general responses
    elif any(word in user_message for word in ['hi', 'hello', 'hey']):
        response = "👋 Hey! Ask me about workouts, nutrition, or exercises!"
    elif any(word in user_message for word in ['thank', 'thanks']):
        response = "You're welcome! 💪"
    elif any(word in user_message for word in ['motivation', 'motivate']):
        response = random.choice(["💪 Consistency beats intensity!", "🚀 Keep going!", "🔥 You've got this!"])
    
    # Default quick response
    else:
        response = "🤖 Ask me about: chest/back/legs workouts, weight loss/muscle gain nutrition, or exercise tips!"
    
    await update.message.reply_text(response)

# Simple HTTP server for health checks
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Bot is healthy!')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        logger.info(f"Health check: {format % args}")

def run_health_server():
    """Run a simple HTTP server for health checks"""
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    logger.info(f"Health server running on port {port}")
    server.serve_forever()

def main() -> None:
    """Start the bot with polling and health server."""
    # Start health server in a separate thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot with polling
    logger.info("🤖 Quick FitCoach AI starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
