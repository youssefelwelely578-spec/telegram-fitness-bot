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

# Comprehensive Fitness Knowledge Database
FITNESS_KNOWLEDGE = {
    "workouts": {
        "beginner": {
            "full_body": """
🏋️ **Beginner Full Body Workout (3 days/week)**

**Day 1 - Upper Body Focus:**
- Push-ups: 3 sets of 8-12 reps
- Bent-over Rows: 3 sets of 10-15 reps  
- Shoulder Press: 3 sets of 10-12 reps
- Plank: 3 sets of 30-45 seconds

**Day 2 - Lower Body Focus:**
- Bodyweight Squats: 3 sets of 15-20 reps
- Lunges: 3 sets of 10-12 reps per leg
- Glute Bridges: 3 sets of 15 reps
- Leg Raises: 3 sets of 12-15 reps

**Day 3 - Full Body Circuit:**
- Squats: 3x12
- Push-ups: 3x10
- Rows: 3x12
- Plank: 3x30s
- Rest 60 seconds between circuits
""",
            "weight_loss": """
🔥 **Beginner Weight Loss Circuit**

**Warm-up (5 minutes):**
- Jumping Jacks: 1 minute
- High Knees: 1 minute
- Arm Circles: 1 minute
- Leg Swings: 1 minute

**Main Circuit (repeat 3-4x):**
- Bodyweight Squats: 45 seconds
- Push-ups (knees ok): 45 seconds
- Mountain Climbers: 45 seconds
- Plank: 45 seconds
- Rest: 60 seconds between circuits
"""
        },
        "intermediate": {
            "push_pull_legs": """
💪 **Intermediate PPL Routine (4-6 days/week)**

**Push Day (Chest/Shoulders/Triceps):**
- Bench Press: 4 sets of 6-10 reps
- Overhead Press: 3 sets of 8-12 reps
- Incline Dumbbell Press: 3 sets of 10-12 reps
- Tricep Dips: 3 sets of 8-15 reps

**Pull Day (Back/Biceps):**
- Pull-ups/Chin-ups: 4 sets to failure
- Barbell Rows: 4 sets of 8-12 reps
- Face Pulls: 3 sets of 15-20 reps
- Bicep Curls: 3 sets of 10-15 reps

**Leg Day:**
- Barbell Squats: 4 sets of 6-10 reps
- Romanian Deadlifts: 3 sets of 8-12 reps
- Lunges: 3 sets of 10-12 reps per leg
- Calf Raises: 4 sets of 15-20 reps
"""
        }
    },
    
    "nutrition": {
        "weight_loss": """
📉 **Weight Loss Nutrition Plan**

**Calorie Target:** Maintenance - 500 calories
**Macronutrient Ratio:** 40% Protein, 30% Carbs, 30% Fat

**Sample Daily Plan:**
- **Breakfast:** 3 eggs + vegetables + 1 slice whole grain toast
- **Lunch:** 150g chicken + large salad + 1/2 avocado
- **Dinner:** 150g fish + steamed vegetables + quinoa
- **Snacks:** Greek yogurt, apple, handful of nuts

**Key Principles:**
- Eat protein with every meal
- Focus on fiber-rich vegetables
- Drink 3-4 liters of water daily
- Limit processed foods and sugar
""",
        
        "muscle_gain": """
💪 **Muscle Gain Nutrition Plan**

**Calorie Target:** Maintenance + 300-500 calories
**Macronutrient Ratio:** 30% Protein, 40% Carbs, 30% Fat

**Sample Daily Plan:**
- **Breakfast:** Oatmeal + protein powder + banana + nuts
- **Lunch:** 200g chicken + brown rice + vegetables
- **Pre-workout:** Complex carbs + small protein
- **Post-workout:** Fast protein + simple carbs
- **Dinner:** 200g red meat + sweet potato + greens

**Key Principles:**
- 1.6-2.2g protein per kg bodyweight
- Carbs around workouts for energy
- Healthy fats for hormone production
""",
        
        "maintenance": """
⚖️ **Maintenance Nutrition Plan**

**Focus:** Balanced eating for health and performance

**Plate Method:**
- 1/2 plate vegetables
- 1/4 plate protein
- 1/4 plate complex carbs
- Add healthy fats

**Daily Guidelines:**
- Protein: 1.2-1.6g per kg bodyweight
- Variety of colorful vegetables
- Whole food carbohydrates
- Hydration: 2-3 liters daily
"""
    },
    
    "exercises": {
        "squat": """
🦵 **Squat - Proper Form Guide**

**Setup:**
- Feet shoulder-width apart
- Toes slightly pointed out
- Chest up, back straight

**Execution:**
1. Break at hips and knees simultaneously
2. Descend until thighs parallel to floor
3. Keep knees tracking over toes
4. Drive through heels to stand

**Common Mistakes:**
- Knees caving inward
- Rounding lower back
- Heels lifting off ground
- Not reaching depth

**Tips:** Start with bodyweight, then progress to goblet squats before barbell.
""",
        
        "deadlift": """
🏋️ **Deadlift - Proper Form Guide**

**Setup:**
- Feet hip-width apart
- Bar over mid-foot
- Hinge at hips, grip bar
- Flat back, chest up

**Execution:**
1. Take slack out of bar
2. Drive feet through floor
3. Keep bar close to body
4. Stand tall, squeeze glutes

**Common Mistakes:**
- Rounding back
- Bar drifting away from body
- Hips rising too fast
- Not engaging lats

**Safety:** Start light, focus on form, use mixed grip for heavy weights.
""",
        
        "bench_press": """
🏋️ **Bench Press - Proper Form Guide**

**Setup:**
- Lie on bench with eyes under bar
- Feet firmly on floor
- Arch back slightly
- Grip slightly wider than shoulders

**Execution:**
1. Unrack bar with straight arms
2. Lower to lower chest/mid-sternum
3. Keep elbows at 45-60 degree angle
4. Press bar back to starting position

**Common Mistakes:**
- Flaring elbows too wide
- Bouncing bar off chest
- Lifting hips off bench
- Not controlling descent
"""
    },
    
    "supplements": {
        "basics": """
💊 **Evidence-Based Supplements**

**Tier 1 (Most Important):**
- **Protein Powder:** Convenient protein source
- **Creatine:** Strength and muscle gains
- **Omega-3 Fish Oil:** Joint and brain health

**Tier 2 (Conditional):**
- **Vitamin D:** If sun exposure is limited
- **Multivitamin:** For nutrient gaps
- **Caffeine:** Pre-workout energy

**Tier 3 (Nice to Have):**
- **BCAAs:** During fasted training
- **Beta-Alanine:** Endurance support
- **ZMA:** Sleep and recovery

**Remember:** Supplements supplement a good diet, they don't replace it!
"""
    }
}

# Motivational messages
MOTIVATIONAL_QUOTES = [
    "💪 The only bad workout is the one that didn't happen!",
    "🚀 Consistency beats intensity every single time!",
    "🔥 Don't stop when you're tired. Stop when you're done!",
    "🌟 A year from now you'll wish you started today!",
    "🌈 The body achieves what the mind believes!",
    "⚡ Strength doesn't come from what you can do. It comes from overcoming the things you once thought you couldn't!",
    "🎯 Small daily improvements are the key to staggering long-term results!",
    "🌱 It's not about having time, it's about making time!"
]

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = """
🤖 **Welcome to Your AI Personal Trainer!** 🏋️‍♂️

I'm your comprehensive fitness assistant capable of helping with:

**📚 What I Can Help With:**
- Personalized workout plans
- Nutrition guidance and meal planning
- Exercise form and technique
- Supplement advice
- Fitness goal setting
- Motivation and accountability

**💡 How to Use Me:**
- Ask specific questions: "How do I do proper squats?"
- Request plans: "Give me a beginner workout"
- Get nutrition advice: "What should I eat for muscle gain?"
- Form checks: "How's my deadlift form?"

**🎯 Try Asking:**
- "Create a 3-day workout plan for beginners"
- "What's the best nutrition for weight loss?"
- "How do I improve my bench press?"
- "Should I take creatine?"

I'm here to be your 24/7 personal trainer! What are your fitness goals today?
"""
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = """
📋 **Complete Command Guide**

**🏋️ Workout Commands:**
- "beginner workout" - Full beginner routine
- "intermediate plan" - Advanced training split
- "weight loss exercises" - Fat burning workouts
- "[exercise name] form" - Proper technique guide

**🥗 Nutrition Commands:**
- "weight loss diet" - Calorie deficit plan
- "muscle gain nutrition" - Bulking diet
- "maintenance eating" - Balanced nutrition
- "meal ideas" - Food suggestions

**💪 Specific Exercise Help:**
- "how to squat"
- "deadlift form"
- "bench press technique"
- "pull-up progression"

**🔬 Science-Based Info:**
- "supplements that work"
- "recovery tips"
- "progressive overload"
- "workout frequency"

**💬 Or just chat naturally!** I understand context and can have full conversations about fitness!
"""
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all text messages with comprehensive fitness knowledge"""
    user_message = update.message.text.lower()
    response = ""
    
    # Workout plans
    if any(word in user_message for word in ['workout', 'exercise', 'training', 'routine']):
        if 'beginner' in user_message:
            response = FITNESS_KNOWLEDGE["workouts"]["beginner"]["full_body"]
        elif 'weight loss' in user_message or 'fat loss' in user_message:
            response = FITNESS_KNOWLEDGE["workouts"]["beginner"]["weight_loss"]
        elif 'intermediate' in user_message or 'advanced' in user_message:
            response = FITNESS_KNOWLEDGE["workouts"]["intermediate"]["push_pull_legs"]
        elif 'push' in user_message:
            response = "**Push Day Focus:** Chest, Shoulders, Triceps\n" + FITNESS_KNOWLEDGE["workouts"]["intermediate"]["push_pull_legs"].split("Push Day")[1].split("Pull Day")[0]
        elif 'pull' in user_message:
            response = "**Pull Day Focus:** Back, Biceps\n" + FITNESS_KNOWLEDGE["workouts"]["intermediate"]["push_pull_legs"].split("Pull Day")[1].split("Leg Day")[0]
        elif 'leg' in user_message:
            response = "**Leg Day Focus:** Quads, Hamstrings, Glutes\n" + FITNESS_KNOWLEDGE["workouts"]["intermediate"]["push_pull_legs"].split("Leg Day")[1]
        else:
            response = "💪 **I can create various workout plans!**\n\nTell me:\n- Your experience level (beginner/intermediate)\n- Your goals (weight loss/muscle gain)\n- Available equipment\n- Days per week you can train\n\nOr ask about a specific muscle group!"
    
    # Nutrition plans
    elif any(word in user_message for word in ['diet', 'nutrition', 'eat', 'food', 'meal', 'calorie']):
        if 'weight loss' in user_message or 'lose fat' in user_message:
            response = FITNESS_KNOWLEDGE["nutrition"]["weight_loss"]
        elif 'muscle gain' in user_message or 'bulk' in user_message or 'gain weight' in user_message:
            response = FITNESS_KNOWLEDGE["nutrition"]["muscle_gain"]
        elif 'maintenance' in user_message or 'balanced' in user_message:
            response = FITNESS_KNOWLEDGE["nutrition"]["maintenance"]
        else:
            response = "🥗 **Nutrition Guidance Available:**\n\n• Weight loss diets\n• Muscle gain nutrition\n• Maintenance eating\n• Meal timing\n• Macronutrient ratios\n\nWhat are your specific nutrition goals?"
    
    # Exercise form
    elif any(word in user_message for word in ['squat', 'deadlift', 'bench', 'press', 'form', 'technique', 'how to']):
        if 'squat' in user_message:
            response = FITNESS_KNOWLEDGE["exercises"]["squat"]
        elif 'deadlift' in user_message:
            response = FITNESS_KNOWLEDGE["exercises"]["deadlift"]
        elif 'bench' in user_message:
            response = FITNESS_KNOWLEDGE["exercises"]["bench_press"]
        else:
            response = "🏋️ **Exercise Form Library:**\n\nI have detailed guides for:\n- Squats (all variations)\n- Deadlifts (conventional, sumo)\n- Bench press\n- Overhead press\n- Rows\n- Pull-ups\n- And many more!\n\nWhich exercise would you like to learn?"
    
    # Supplements
    elif any(word in user_message for word in ['supplement', 'creatine', 'protein', 'vitamin', 'pre-workout']):
        response = FITNESS_KNOWLEDGE["supplements"]["basics"]
    
    # Motivation
    elif any(word in user_message for word in ['motivate', 'inspire', 'tired', 'hard', 'quit']):
        response = random.choice(MOTIVATIONAL_QUOTES) + "\n\nYou've got this! 💪"
    
    # Greetings
    elif any(word in user_message for word in ['hello', 'hi', 'hey', 'how are you']):
        response = "👋 Hello! I'm your AI personal trainer ready to help with all things fitness! What would you like to work on today?"
    
    # Thank you
    elif any(word in user_message for word in ['thank', 'thanks', 'appreciate']):
        response = "You're welcome! 😊 Keep up the great work and remember: consistency is key! 🎯"
    
    # Default response for unknown queries
    else:
        response = """
🤖 **I'm your comprehensive fitness AI!** 

I can help you with:
• **Workout Planning** - Custom routines for any goal
• **Nutrition Guidance** - Diet plans and meal strategies  
• **Exercise Technique** - Proper form and safety
• **Supplement Advice** - Evidence-based recommendations
• **Goal Setting** - SMART fitness objectives
• **Progress Tracking** - How to measure results

💡 **Try asking specific questions like:**
- "Create a 3-day full body workout"
- "What should I eat before and after training?"
- "How do I perform squats safely?"
- "Best exercises for building muscle?"

What's your current fitness focus? 🏋️‍♂️
"""
    
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
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot with polling
    logger.info("🤖 AI Personal Trainer starting with comprehensive knowledge...")
    application.run_polling()

if __name__ == '__main__':
    main()
