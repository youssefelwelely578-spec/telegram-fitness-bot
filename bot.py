import os
import logging
import time
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import signal
import sys

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    logger.error("BOT_TOKEN environment variable not set!")
    sys.exit(1)

# Store user data for personalized plans
user_data = {}

# Comprehensive Exercise Database (same as before)
EXERCISE_DATABASE = {
    "chest": [
        {"name": "Bench Press", "type": "Compound", "equipment": "Barbell/Bench", "sets_reps": "4x6-12"},
        {"name": "Incline Dumbbell Press", "type": "Compound", "equipment": "Dumbbells/Bench", "sets_reps": "3x8-12"},
        {"name": "Cable Fly", "type": "Isolation", "equipment": "Cable Machine", "sets_reps": "3x12-15"},
        {"name": "Push-ups", "type": "Compound", "equipment": "Bodyweight", "sets_reps": "3x15-20"},
        {"name": "Pec Deck", "type": "Isolation", "equipment": "Machine", "sets_reps": "3x12-15"}
    ],
    # ... (rest of your exercise database remains the same)
}

# Training Splits (same as before)
TRAINING_SPLITS = {
    "full_body": {
        "name": "Full Body",
        "days": "3-4 days/week",
        "description": "Exercises for all major muscles each session",
        "sample": """
**Full Body Sample Day:**
• Squats: 3x8
• Bench Press: 3x8
• Pull-ups: 3x8
• Overhead Press: 3x8
• Plank: 3x60sec
"""
    },
    # ... (rest of your training splits remain the same)
}

class BotManager:
    def __init__(self, token):
        self.token = token
        self.application = None
        self.is_running = False
        
    async def initialize_bot(self):
        """Initialize the bot application"""
        try:
            self.application = Application.builder().token(self.token).build()
            
            # Add handlers
            self.application.add_handler(CommandHandler("start", start))
            self.application.add_handler(CommandHandler("status", status))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
            
            # Add error handler
            self.application.add_error_handler(error_handler)
            
            logger.info("Bot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            return False
    
    async def start_polling(self):
        """Start the bot with polling"""
        if not self.application:
            if not await self.initialize_bot():
                return False
        
        try:
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES
            )
            
            self.is_running = True
            logger.info("Bot started polling successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start polling: {e}")
            self.is_running = False
            return False
    
    async def stop_polling(self):
        """Stop the bot gracefully"""
        try:
            if self.application and self.application.updater:
                await self.application.updater.stop()
            if self.application:
                await self.application.stop()
                await self.application.shutdown()
            
            self.is_running = False
            logger.info("Bot stopped gracefully")
            
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
    
    async def restart_bot(self):
        """Restart the bot"""
        logger.info("Restarting bot...")
        await self.stop_polling()
        await asyncio.sleep(2)  # Wait a bit before restarting
        return await self.start_polling()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏋️ **Your AI Personal Trainer**\n\n"
        "I can help you with:\n"
        "• Complete workout programs & training splits\n"
        "• Exercise database with 100+ exercises\n"
        "• Personalized diet & nutrition plans\n"
        "• Muscle anatomy & exercise form\n"
        "• Recovery, hydration & supplements\n\n"
        "Use commands like:\n"
        "• 'chest exercises'\n• 'full body workout'\n• 'diet plan'\n• 'supplements'\n• 'training splits'"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check bot status"""
    await update.message.reply_text("✅ Bot is running smoothly! How can I help you with your fitness goals today?")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors in telegram bot"""
    logger.error(f"Exception while handling an update: {context.error}")
    
    # Try to notify user about error
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Sorry, I encountered an error. Please try again in a moment."
            )
    except Exception as e:
        logger.error(f"Error while sending error message: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages with error handling"""
    try:
        user_message = update.message.text.lower()
        user_id = update.message.from_user.id
        
        # Store conversation context
        if user_id not in user_data:
            user_data[user_id] = {"diet_info": {}}
        
        # === EXERCISE DATABASE QUERIES ===
        for muscle_group, exercises in EXERCISE_DATABASE.items():
            if muscle_group in user_message and any(word in user_message for word in ['exercise', 'movement', 'workout']):
                response = f"💪 **{muscle_group.title()} Exercises**\n\n"
                for exercise in exercises:
                    response += f"• **{exercise['name']}** ({exercise['type']})\n"
                    response += f"  Equipment: {exercise['equipment']}\n"
                    response += f"  Sets/Reps: {exercise['sets_reps']}\n\n"
                await update.message.reply_text(response)
                return
        
        # === TRAINING SPLITS ===
        if any(word in user_message for word in ['split', 'routine', 'program', 'schedule']):
            if 'full' in user_message and 'body' in user_message:
                split = TRAINING_SPLITS["full_body"]
            elif 'upper' in user_message and 'lower' in user_message:
                split = TRAINING_SPLITS["upper_lower"]
            elif 'push' in user_message and 'pull' in user_message:
                split = TRAINING_SPLITS["ppl"]
            elif 'bro' in user_message:
                split = TRAINING_SPLITS["bro_split"]
            else:
                # Show all splits
                response = "🏋️ **Training Splits Available:**\n\n"
                for key, split_info in TRAINING_SPLITS.items():
                    response += f"• **{split_info['name']}** ({split_info['days']})\n"
                    response += f"  {split_info['description']}\n\n"
                response += "Ask about any specific split for details!"
                await update.message.reply_text(response)
                return
            
            response = f"📅 **{split['name']} Split**\n\n"
            response += f"**Frequency:** {split['days']}\n"
            response += f"**Description:** {split['description']}\n\n"
            response += split['sample']
            await update.message.reply_text(response)
            return
        
        # === ANATOMY & MUSCLE GROUPS ===
        if any(word in user_message for word in ['anatomy', 'muscle', 'muscles']):
            await update.message.reply_text("""
🔬 **Major Muscle Groups Anatomy:**

**Upper Body:**
• **Chest:** Pectoralis major & minor
• **Back:** Latissimus dorsi, trapezius, rhomboids, erector spinae
• **Shoulders:** Deltoids (anterior, medial, posterior), rotator cuff
• **Arms:** Biceps, Triceps, Forearms

**Lower Body:**
• **Legs:** Quadriceps, hamstrings, glutes, calves
• **Core:** Rectus abdominis, obliques, transverse abdominis, lower back

Ask about specific muscle groups for exercises!
""")
            return
        
        # === CARDIO & CONDITIONING ===
        if 'cardio' in user_message:
            await update.message.reply_text("""
🏃 **Cardio & Conditioning Guidelines**

**LISS (Low Intensity Steady State):**
• Walking, cycling, swimming
• 30-60 minutes, 3-5x/week
• 60-70% max heart rate

**HIIT (High Intensity Interval Training):**
• Sprints, circuit training, burpees
• 20-30 minutes, 2-3x/week
• 80-90% max heart rate intervals

**Active Recovery:**
• Yoga, mobility work, foam rolling
• Light activity on rest days

**Benefits:** Improved endurance, fat loss, heart health
""")
            return
        
        # === RECOVERY & INJURY PREVENTION ===
        if any(word in user_message for word in ['recovery', 'rest', 'sleep', 'injury']):
            await update.message.reply_text("""
😴 **Recovery & Injury Prevention**

**Essential Recovery:**
• Sleep: 7-9 hours/night
• Stretch pre/post-workout
• Foam roll & mobilize joints
• Progressive overload for safe growth

**Injury Prevention:**
• Proper warm-up (5-10 min dynamic stretching)
• Maintain proper form always
• Listen to your body - don't train through pain
• Balance pushing limits with smart training

**Signs of Overtraining:**
• Fatigue, poor performance, irritability
• Insomnia, decreased immunity
• Plateau or regression in strength
""")
            return
        
        # === HYDRATION & SUPPLEMENTS ===
        if any(word in user_message for word in ['supplement', 'supplements']):
            await update.message.reply_text("""
💊 **Evidence-Based Supplements**

**Tier 1 (Most Beneficial):**
• **Protein Powder:** 20-40g post-workout
• **Creatine Monohydrate:** 5g daily for strength & muscle
• **Omega-3 Fish Oil:** Joint & brain health

**Tier 2 (Conditional):**
• **Vitamin D:** If limited sun exposure
• **Multivitamin:** Nutrient insurance
• **Caffeine:** 200-400mg pre-workout

**Tier 3 (Nice to Have):**
• **BCAAs/EAAs:** During fasted training
• **Beta-Alanine:** Endurance support
• **Electrolytes:** For heavy sweaters

**Hydration:** 30-40 ml/kg body weight daily
""")
            return
        
        if any(word in user_message for word in ['water', 'hydrate', 'hydration']):
            await update.message.reply_text("""
💧 **Hydration Guidelines**

**Daily Intake:** 30-40 ml per kg body weight
**Example:** 75kg person = 2.25-3 liters daily

**During Exercise:** 500ml-1 liter per hour
**Electrolytes Needed:** Sodium, potassium, magnesium

**Signs of Dehydration:**
• Dark urine, fatigue, headaches
• Muscle cramps, dizziness

**Benefits:** Performance, recovery, joint health, temperature regulation
""")
            return
        
        # === NUTRITION & DIET PLANS ===
        if any(word in user_message for word in ['diet', 'nutrition', 'eat', 'food', 'meal', 'macro']):
            if 'diet plan' in user_message or 'personalized' in user_message:
                user_data[user_id]["waiting_for_info"] = True
                await update.message.reply_text("""
🥗 **Personalized Diet Plan Creator**

To create your custom plan, I need:
1. **Age:** 
2. **Weight (kg):** 
3. **Height (cm):** 
4. **Activity Level** (sedentary/light/moderate/active/very active):
5. **Goal** (weight loss/muscle gain/maintenance):

**Example:** "I'm 25, 75kg, 180cm, moderate activity, want muscle gain"

Tell me your details one by one or all together!
""")
                return
            
            # General nutrition guidelines
            await update.message.reply_text("""
🥗 **Nutrition & Meal Planning**

**Macros (per kg body weight):**
• **Protein:** 1.6-2.2g → Muscle gain & repair
• **Carbs:** 3-6g → Energy for workouts  
• **Fats:** 0.8-1g → Hormones & cell health

**Meal Timing:**
• Pre-workout: Carbs + moderate protein
• Post-workout: Protein + carbs within 1-2 hours

**Foods to Include:**
• Lean meats, fish, eggs, dairy
• Whole grains: oats, rice, quinoa
• Fruits & vegetables (all colors)
• Healthy fats: nuts, seeds, olive oil, avocado

**Foods to Avoid:**
• Sugary drinks & snacks
• Excessive processed foods
• Trans fats & deep-fried foods

Ask for 'diet plan' for personalized calculations!
""")
            return
        
        # === MINDSET & MOTIVATION ===
        if any(word in user_message for word in ['motivation', 'mindset', 'goal', 'progress']):
            await update.message.reply_text("""
🎯 **Mindset & Motivation**

**SMART Goals:**
• **Specific:** Clear, defined objectives
• **Measurable:** Trackable progress
• **Achievable:** Realistic targets
• **Relevant:** Aligned with your values
• **Time-bound:** Set deadlines

**Success Habits:**
• Track progress consistently
• Focus on consistency over perfection
• Adjust when progress stalls
• Balance fitness with lifestyle
• Manage stress effectively

**Remember:** Fitness is a marathon, not a sprint!
""")
            return
        
        # === PERSONALIZED DIET INFO COLLECTION ===
        if user_data[user_id].get("waiting_for_info", False):
            # Simple pattern matching for diet info
            if any(word in user_message for word in ['25', '30', '35', '40', '45', '50']):  # Age
                user_data[user_id]["diet_info"]["age"] = user_message
            elif any(word in user_message for word in ['70', '75', '80', '85', '90', '95', '100']):  # Weight
                user_data[user_id]["diet_info"]["weight"] = user_message
            elif any(word in user_message for word in ['170', '175', '180', '185', '190', '195']):  # Height
                user_data[user_id]["diet_info"]["height"] = user_message
            elif any(word in user_message for word in ['moderate', 'active', 'sedentary', 'light']):  # Activity
                user_data[user_id]["diet_info"]["activity"] = user_message
            elif any(word in user_message for word in ['muscle gain', 'weight loss', 'maintenance']):  # Goal
                user_data[user_id]["diet_info"]["goal"] = user_message
                # Generate diet plan when all info is collected
                await generate_diet_plan(update, user_data[user_id]["diet_info"])
                user_data[user_id]["waiting_for_info"] = False
            else:
                await update.message.reply_text("Please provide: age, weight, height, activity level, and goal.")
            return
        
        # === GREETINGS & DEFAULT ===
        if any(word in user_message for word in ['hi', 'hello', 'hey']):
            await update.message.reply_text("👋 Hey! I'm your AI personal trainer. Ask me about workouts, nutrition, or fitness goals!")
            return
        
        elif any(word in user_message for word in ['thank', 'thanks']):
            await update.message.reply_text("You're welcome! 💪 Keep crushing your fitness goals!")
            return
        
        else:
            await update.message.reply_text("""
🤔 **How can I help you today?**

**Workout Programs:**
• "chest exercises", "back workouts", "leg day"
• "training splits", "full body routine", "push pull legs"

**Nutrition & Diet:**
• "diet plan", "nutrition guidelines", "macros"
• "supplements", "hydration"

**General Fitness:**
• "anatomy", "muscle groups"
• "cardio", "recovery", "mindset"

Ask me anything specific!
""")
            
    except Exception as e:
        logger.error(f"Error in handle_message: {e}")
        try:
            await update.message.reply_text("❌ Sorry, I encountered an error processing your request. Please try again.")
        except:
            pass

async def generate_diet_plan(update: Update, diet_info):
    """Generate personalized diet plan based on user info"""
    try:
        age = diet_info.get('age', '30')
        weight = diet_info.get('weight', '75')
        height = diet_info.get('height', '180')
        activity = diet_info.get('activity', 'moderate')
        goal = diet_info.get('goal', 'muscle gain')
        
        # Calculate macros based on Chapter 7 guidelines
        protein = float(weight) * 2.0  # 2g/kg for optimal muscle growth
        if 'loss' in goal:
            carbs = float(weight) * 3.0
            fats = float(weight) * 0.8
        elif 'gain' in goal:
            carbs = float(weight) * 5.0
            fats = float(weight) * 1.0
        else:  # maintenance
            carbs = float(weight) * 4.0
            fats = float(weight) * 0.9
        
        calories = calculate_calories(weight, activity, goal)
        
        plan = f"""
🥗 **Personalized Diet Plan**

**Based on your info:**
• Age: {age}
• Weight: {weight}kg
• Height: {height}cm  
• Activity: {activity}
• Goal: {goal}

**Daily Targets:**
• Calories: {calories}
• Protein: {protein:.0f}g ({protein*4:.0f} cal)
• Carbs: {carbs:.0f}g ({carbs*4:.0f} cal)
• Fats: {fats:.0f}g ({fats*9:.0f} cal)

**Sample Meal Plan:**
**Breakfast:** Oatmeal + protein powder + berries
**Lunch:** Chicken + rice + vegetables + avocado  
**Dinner:** Fish + sweet potato + green vegetables
**Snacks:** Greek yogurt, nuts, fruits

**Hydration:** {float(weight)*35/1000:.1f} liters water daily
**Timing:** Protein every 3-4 hours, carbs around workouts
"""
        await update.message.reply_text(plan)
    except Exception as e:
        logger.error(f"Error generating diet plan: {e}")
        await update.message.reply_text("❌ Error generating diet plan. Please try again.")

def calculate_calories(weight, activity, goal):
    # Using established formulas from knowledge base
    base = float(weight) * 30  # Base metabolic estimate
    
    # Activity multipliers
    if 'sedentary' in activity: base *= 1.2
    elif 'light' in activity: base *= 1.375
    elif 'moderate' in activity: base *= 1.55
    elif 'active' in activity: base *= 1.725
    else: base *= 1.9  # very active
    
    # Goal adjustments
    if 'loss' in goal: base -= 500
    elif 'gain' in goal: base += 300
    
    return int(base)

async def run_bot():
    """Main bot running function with robust error handling"""
    bot_manager = BotManager(BOT_TOKEN)
    
    restart_attempts = 0
    max_restart_attempts = 10
    
    while restart_attempts < max_restart_attempts:
        try:
            logger.info(f"Starting bot (attempt {restart_attempts + 1})...")
            
            if await bot_manager.start_polling():
                logger.info("Bot is now running. Press Ctrl+C to stop.")
                
                # Keep the bot running until stopped
                while bot_manager.is_running:
                    await asyncio.sleep(10)  # Check every 10 seconds
                    
                    # Optional: Add health check here
                    if restart_attempts > 0:
                        logger.info("Bot recovered successfully")
                        restart_attempts = 0  # Reset counter after successful recovery
                        
            else:
                logger.error("Failed to start bot")
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal. Shutting down...")
            await bot_manager.stop_polling()
            break
            
        except Exception as e:
            logger.error(f"Bot crashed with error: {e}")
            restart_attempts += 1
            
            if restart_attempts >= max_restart_attempts:
                logger.error("Max restart attempts reached. Giving up.")
                break
                
            wait_time = min(30, 5 * restart_attempts)  # Exponential backoff, max 30 seconds
            logger.info(f"Restarting in {wait_time} seconds...")
            await asyncio.sleep(wait_time)
            
            # Try to restart
            await bot_manager.stop_polling()
            
    logger.info("Bot has stopped.")

def main():
    """Main entry point"""
    try:
        # Run the bot
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
    finally:
        logger.info("Bot process ended")

if __name__ == '__main__':
    main()
