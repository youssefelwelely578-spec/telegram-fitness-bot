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

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

# Comprehensive Knowledge Database
KNOWLEDGE_BASE = {
    "water": "💧 **Water Intake:** 3-4 liters daily. More if you're active/sweating. Drink throughout the day, not all at once.",
    
    "post_workout": "🥗 **Post-Workout Nutrition:** Protein + carbs within 1-2 hours. Examples: protein shake + banana, chicken + rice, Greek yogurt + fruits.",
    
    "pre_workout": "⚡ **Pre-Workout:** Carbs + protein 1-2 hours before. Examples: oatmeal + protein, banana + peanut butter, rice + chicken.",
    
    "protein": "💪 **Protein:** 1.6-2.2g per kg bodyweight. Sources: chicken, fish, eggs, Greek yogurt, protein powder, lentils.",
    
    "sleep": "😴 **Sleep:** 7-9 hours nightly for recovery. Quality sleep boosts muscle growth, hormone production, and performance.",
    
    "cardio": "🏃 **Cardio:** 150 mins moderate or 75 mins vigorous weekly. Can be walking, running, cycling, swimming.",
    
    "recovery": "🔄 **Recovery:** 48 hours between training same muscle groups. Active recovery: light walking, stretching, foam rolling.",
    
    "supplements": "💊 **Supplements:** Protein powder, creatine, omega-3s are most evidence-based. Food first, supplements second."
}

WORKOUTS = {
    "chest": "💪 **Chest:** Bench Press 4x8, Incline Press 3x10, Flyes 3x12, Push-ups 3x failure",
    "back": "💪 **Back:** Pull-ups 4x8, Rows 4x10, Pulldowns 3x12, Face Pulls 3x15",
    "biceps": "💪 **Biceps:** Curls 4x10, Hammer Curls 3x12, Concentration Curls 3x15",
    "triceps": "💪 **Triceps:** Pushdowns 4x12, Overhead Extension 3x10, Dips 3x15",
    "shoulders": "💪 **Shoulders:** OHP 4x8, Lateral Raises 3x15, Front Raises 3x12",
    "legs": "🦵 **Legs:** Squats 4x8, Deadlifts 3x6, Lunges 3x10, Calf Raises 4x15"
}

NUTRITION = {
    "weight_loss": "📉 **Weight Loss:** Calorie deficit, high protein (2g/kg), veggies, limit processed foods, stay hydrated",
    "muscle_gain": "💪 **Muscle Gain:** Calorie surplus, protein (2g/kg), carbs around workouts, progressive overload"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🤖 **FITCOACH AI** - Your Smart Fitness Assistant\n\n"
        "I understand natural language! Ask me:\n"
        "• Workout plans (chest, back, legs, etc.)\n"
        "• Nutrition advice (what to eat, when to eat)\n" 
        "• General fitness questions\n"
        "• Exercise tips and form\n\n"
        "Try: 'how much water to drink', 'what to eat after gym', 'protein requirements'"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text.lower()
    response = ""
    
    # General knowledge questions - CHECK THESE FIRST
    if any(word in user_message for word in ['water', 'drink', 'hydrate', 'liter', 'litre']):
        response = KNOWLEDGE_BASE["water"]
    
    elif any(word in user_message for word in ['after gym', 'after workout', 'post workout', 'post gym']):
        response = KNOWLEDGE_BASE["post_workout"]
    
    elif any(word in user_message for word in ['before gym', 'pre workout', 'before workout']):
        response = KNOWLEDGE_BASE["pre_workout"]
    
    elif any(word in user_message for word in ['protein', 'how much protein']):
        response = KNOWLEDGE_BASE["protein"]
    
    elif any(word in user_message for word in ['sleep', 'rest', 'recover']):
        response = KNOWLEDGE_BASE["sleep"]
    
    elif any(word in user_message for word in ['cardio', 'running', 'cycling']):
        response = KNOWLEDGE_BASE["cardio"]
    
    elif any(word in user_message for word in ['recovery', 'rest day']):
        response = KNOWLEDGE_BASE["recovery"]
    
    elif any(word in user_message for word in ['supplement', 'creatine', 'pre-workout']):
        response = KNOWLEDGE_BASE["supplements"]
    
    # Workout plans
    elif any(word in user_message for word in ['chest', 'bench', 'push']):
        response = WORKOUTS["chest"]
    
    elif any(word in user_message for word in ['back', 'pull', 'row']):
        response = WORKOUTS["back"]
    
    elif any(word in user_message for word in ['bicep', 'curl']):
        response = WORKOUTS["biceps"]
    
    elif any(word in user_message for word in ['tricep', 'pushdown']):
        response = WORKOUTS["triceps"]
    
    elif any(word in user_message for word in ['shoulder', 'delt']):
        response = WORKOUTS["shoulders"]
    
    elif any(word in user_message for word in ['leg', 'squat', 'deadlift']):
        response = WORKOUTS["legs"]
    
    # Nutrition plans
    elif any(word in user_message for word in ['weight loss', 'lose fat', 'burn fat']):
        response = NUTRITION["weight_loss"]
    
    elif any(word in user_message for word in ['muscle gain', 'bulk', 'gain muscle']):
        response = NUTRITION["muscle_gain"]
    
    # Diet plan
    elif any(word in user_message for word in ['diet plan', 'personalized', 'custom']):
        response = "🥗 **Personalized Diet Plan:** Tell me your age, weight, height, activity level, and goals for a custom plan!"
    
    # Greetings
    elif any(word in user_message for word in ['hi', 'hello', 'hey', 'how are you']):
        response = "👋 Hello! I'm your AI fitness coach. Ask me anything about workouts, nutrition, or general fitness!"
    
    # Thank you
    elif any(word in user_message for word in ['thank', 'thanks', 'appreciate']):
        response = "You're welcome! 💪 Keep up the great work!"
    
    # Motivation
    elif any(word in user_message for word in ['motivate', 'tired', 'hard', 'quit']):
        responses = [
            "💪 Consistency beats intensity! Keep showing up!",
            "🚀 Progress takes time - trust the process!",
            "🔥 The only bad workout is the one that didn't happen!",
            "🌟 You're stronger than you think!",
            "🎯 Small daily improvements lead to big results!"
        ]
        response = random.choice(responses)
    
    # Default response for unknown questions
    else:
        response = (
            "🤖 I'm your fitness AI! Try asking about:\n\n"
            "💧 **Hydration:** 'How much water should I drink?'\n"
            "🥗 **Nutrition:** 'What to eat after workout?'\n" 
            "💪 **Workouts:** 'Chest workout', 'Back exercises'\n"
            "📊 **General:** 'Protein needs', 'Recovery tips'\n\n"
            "Or be more specific with your question!"
        )
    
    await update.message.reply_text(response)

# Health server
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
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    import time
    while True:
        try:
            logger.info("🤖 Smart FitCoach AI starting...")
            application.run_polling(drop_pending_updates=True)
        except Exception as e:
            logger.error(f"Error: {e}. Restarting in 5 seconds...")
            time.sleep(5)

if __name__ == '__main__':
    main()
