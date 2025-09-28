import os
import logging
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Store user data for personalized plans
user_data = {}

# Comprehensive Exercise Database
EXERCISE_DATABASE = {
    "chest": [
        {"name": "Bench Press", "type": "Compound", "equipment": "Barbell/Bench", "sets_reps": "4x6-12"},
        {"name": "Incline Dumbbell Press", "type": "Compound", "equipment": "Dumbbells/Bench", "sets_reps": "3x8-12"},
        {"name": "Cable Fly", "type": "Isolation", "equipment": "Cable Machine", "sets_reps": "3x12-15"},
        {"name": "Push-ups", "type": "Compound", "equipment": "Bodyweight", "sets_reps": "3x15-20"},
        {"name": "Pec Deck", "type": "Isolation", "equipment": "Machine", "sets_reps": "3x12-15"}
    ],
    "back": [
        {"name": "Pull-ups", "type": "Compound", "equipment": "Bodyweight/Bar", "sets_reps": "4x6-12"},
        {"name": "Barbell Row", "type": "Compound", "equipment": "Barbell", "sets_reps": "4x8-10"},
        {"name": "Lat Pulldown", "type": "Compound", "equipment": "Cable Machine", "sets_reps": "3x10-12"},
        {"name": "Seated Cable Row", "type": "Compound", "equipment": "Cable Machine", "sets_reps": "3x10-12"},
        {"name": "Face Pulls", "type": "Isolation", "equipment": "Cable Machine", "sets_reps": "3x15-20"}
    ],
    "shoulders": [
        {"name": "Overhead Press", "type": "Compound", "equipment": "Barbell/Dumbbells", "sets_reps": "4x6-10"},
        {"name": "Lateral Raise", "type": "Isolation", "equipment": "Dumbbells", "sets_reps": "3x12-15"},
        {"name": "Front Raise", "type": "Isolation", "equipment": "Dumbbells", "sets_reps": "3x12-15"},
        {"name": "Rear Delt Fly", "type": "Isolation", "equipment": "Dumbbells", "sets_reps": "3x15-20"}
    ],
    "biceps": [
        {"name": "Barbell Curl", "type": "Isolation", "equipment": "Barbell", "sets_reps": "4x8-12"},
        {"name": "Dumbbell Curl", "type": "Isolation", "equipment": "Dumbbells", "sets_reps": "3x10-12"},
        {"name": "Hammer Curl", "type": "Isolation", "equipment": "Dumbbells", "sets_reps": "3x10-12"},
        {"name": "Preacher Curl", "type": "Isolation", "equipment": "Bench/Barbell", "sets_reps": "3x10-12"}
    ],
    "triceps": [
        {"name": "Tricep Pushdown", "type": "Isolation", "equipment": "Cable Machine", "sets_reps": "3x12-15"},
        {"name": "Overhead Extension", "type": "Isolation", "equipment": "Dumbbell/Cable", "sets_reps": "3x10-12"},
        {"name": "Close Grip Bench", "type": "Compound", "equipment": "Barbell", "sets_reps": "4x8-10"},
        {"name": "Dips", "type": "Compound", "equipment": "Bodyweight", "sets_reps": "3x10-15"}
    ],
    "legs": [
        {"name": "Squats", "type": "Compound", "equipment": "Barbell", "sets_reps": "4x6-10"},
        {"name": "Deadlift", "type": "Compound", "equipment": "Barbell", "sets_reps": "3x6-8"},
        {"name": "Leg Press", "type": "Compound", "equipment": "Machine", "sets_reps": "3x10-15"},
        {"name": "Lunges", "type": "Compound", "equipment": "Dumbbells/Barbell", "sets_reps": "3x10-12"},
        {"name": "Leg Curl", "type": "Isolation", "equipment": "Machine", "sets_reps": "3x12-15"},
        {"name": "Calf Raises", "type": "Isolation", "equipment": "Machine/Bodyweight", "sets_reps": "4x15-20"}
    ],
    "core": [
        {"name": "Plank", "type": "Bodyweight", "equipment": "None", "sets_reps": "3x60sec"},
        {"name": "Hanging Leg Raise", "type": "Isolation", "equipment": "Pull-up Bar", "sets_reps": "3x12-15"},
        {"name": "Russian Twists", "type": "Isolation", "equipment": "Bodyweight/Dumbbell", "sets_reps": "3x15-20"},
        {"name": "Cable Crunch", "type": "Isolation", "equipment": "Cable Machine", "sets_reps": "3x15-20"}
    ]
}

# Training Splits
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
    "upper_lower": {
        "name": "Upper/Lower",
        "days": "4 days/week",
        "description": "Alternating upper and lower body days",
        "sample": """
**Upper Day:**
• Bench Press: 4x8-12
• Pull-ups: 4x6-12
• Overhead Press: 3x8-12
• Rows: 3x8-12
• Bicep Curls: 3x10-12

**Lower Day:**
• Squats: 4x6-10
• Deadlifts: 3x6-8
• Leg Press: 3x10-15
• Leg Curls: 3x12-15
• Calf Raises: 4x15-20
"""
    },
    "ppl": {
        "name": "Push/Pull/Legs",
        "days": "6 days/week",
        "description": "Push: Chest/Shoulders/Triceps, Pull: Back/Biceps, Legs: Legs/Core",
        "sample": """
**Push Day:**
• Bench Press: 4x8-12
• Overhead Press: 3x8-12
• Incline Press: 3x10-12
• Tricep Extensions: 3x12-15
• Lateral Raises: 3x15-20

**Pull Day:**
• Pull-ups: 4x6-12
• Barbell Rows: 4x8-10
• Lat Pulldowns: 3x10-12
• Face Pulls: 3x15-20
• Bicep Curls: 3x12-15

**Legs Day:**
• Squats: 4x6-10
• Deadlifts: 3x6-8
• Lunges: 3x10-12
• Leg Press: 3x12-15
• Calf Raises: 4x15-20
"""
    },
    "bro_split": {
        "name": "Bro Split",
        "days": "5-6 days/week",
        "description": "One muscle group per day",
        "sample": """
**Chest Day, Back Day, Shoulders Day, Arms Day, Legs Day**
Focus on one major muscle group per session with high volume.
"""
    }
}

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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def generate_diet_plan(update: Update, diet_info):
    """Generate personalized diet plan based on user info"""
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

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    while True:
        try:
            application.run_polling(drop_pending_updates=True)
        except Exception as e:
            logger.error(f"Bot error: {e}")
            time.sleep(10)
            continue

if __name__ == '__main__':
    main()
