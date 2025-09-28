import os
import logging
import threading
import time
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
    "chest": "💪 **Chest:** Bench Press 4x8, Incline Press 3x10, Flyes 3x12, Push-ups 3x failure",
    "back": "💪 **Back:** Pull-ups 4x8, Rows 4x10, Pulldowns 3x12, Face Pulls 3x15",
    "legs": "🦵 **Legs:** Squats 4x8, Deadlifts 3x6, Lunges 3x10, Leg Press 3x12",
    "shoulders": "💪 **Shoulders:** OHP 4x8, Lateral Raises 3x12, Front Raises 3x12",
    "arms": "💪 **Arms:** Curls 3x12, Tricep Pushdowns 3x12, Hammer Curls 3x10"
}

NUTRITION = {
    "weight loss": "📉 **Weight Loss:** Calorie deficit, high protein, veggies, limit processed foods",
    "muscle gain": "💪 **Muscle Gain:** Calorie surplus, protein 2g/kg, carbs around workouts",
    "maintenance": "⚖️ **Maintenance:** Balanced diet, protein 1.6g/kg, variety of foods"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🤖 **FitCoach AI** - Ask: chest/back/legs workout or weight loss/muscle gain nutrition")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text.lower()
    
    if 'chest' in user_message:
        await update.message.reply_text(WORKOUTS["chest"])
    elif 'back' in user_message:
        await update.message.reply_text(WORKOUTS["back"])
    elif 'leg' in user_message:
        await update.message.reply_text(WORKOUTS["legs"])
    elif 'shoulder' in user_message:
        await update.message.reply_text(WORKOUTS["shoulders"])
    elif 'arm' in user_message:
        await update.message.reply_text(WORKOUTS["arms"])
    elif 'weight loss' in user_message:
        await update.message.reply_text(NUTRITION["weight loss"])
    elif 'muscle gain' in user_message:
        await update.message.reply_text(NUTRITION["muscle gain"])
    elif 'hi' in user_message:
        await update.message.reply_text("👋 Ask me about workouts or nutrition!")
    else:
        await update.message.reply_text("💪 Ask: chest/back/legs workout or weight loss nutrition")

# Simple HTTP server for health checks
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
        return  # Disable logging

def run_health_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

def main():
    # Start health server
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # Create application with conflict handling
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start with error handling and auto-restart
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logger.info("Starting bot...")
            application.run_polling(
                drop_pending_updates=True,
                close_loop=False
            )
        except Exception as e:
            logger.error(f"Bot crashed: {e}")
            retry_count += 1
            if retry_count < max_retries:
                logger.info(f"Restarting in 10 seconds... (Attempt {retry_count}/{max_retries})")
                time.sleep(10)
            else:
                logger.error("Max retries reached. Bot stopped.")
                break

if __name__ == '__main__':
    main()
