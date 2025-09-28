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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏋️ **Your AI Personal Trainer**\n\n"
        "I can help you with:\n"
        "• Complete workout programs\n"
        "• Personalized diet plans\n"
        "• Exercise form and technique\n"
        "• Nutrition and supplementation\n"
        "• Fitness goals and tracking\n\n"
        "Just ask me anything fitness-related!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.lower()
    user_id = update.message.from_user.id
    
    # Store conversation context
    if user_id not in user_data:
        user_data[user_id] = {"diet_info": {}}
    
    # === WORKOUT PROGRAMS ===
    if any(word in user_message for word in ['workout', 'exercise', 'training', 'routine', 'program']):
        # Push/Pull/Legs
        if 'push' in user_message and 'pull' in user_message:
            await update.message.reply_text("""
💪 **Push/Pull/Legs (PPL) Program**

**Push Days (Chest/Shoulders/Triceps):**
• Bench Press: 4x8-12
• Overhead Press: 3x8-12
• Incline Press: 3x10-12
• Tricep Extensions: 3x12-15
• Lateral Raises: 3x15-20

**Pull Days (Back/Biceps):**
• Pull-ups: 4x6-12
• Barbell Rows: 4x8-10
• Lat Pulldowns: 3x10-12
• Face Pulls: 3x15-20
• Bicep Curls: 3x12-15

**Leg Days:**
• Squats: 4x6-10
• Deadlifts: 3x6-8
• Lunges: 3x10-12
• Leg Press: 3x12-15
• Calf Raises: 4x15-20

**Frequency:** 3-6 days weekly
""")
        
        # Chest + Biceps
        elif 'chest' in user_message and 'bicep' in user_message:
            await update.message.reply_text("""
💪 **Chest & Biceps Day**

**Chest Exercises:**
• Bench Press: 4x8-12
• Incline Dumbbell Press: 3x10-12
• Chest Flyes: 3x12-15
• Cable Crossovers: 3x12-15

**Biceps Exercises:**
• Barbell Curls: 4x10-12
• Hammer Curls: 3x10-12
• Concentration Curls: 3x12-15
• Preacher Curls: 3x10-12

**Tips:** Start with compound movements, finish with isolation.
""")
        
        # Back + Triceps
        elif 'back' in user_message and 'tricep' in user_message:
            await update.message.reply_text("""
💪 **Back & Triceps Day**

**Back Exercises:**
• Pull-ups: 4x6-12
• Bent-over Rows: 4x8-10
• Seated Rows: 3x10-12
• Lat Pulldowns: 3x10-12

**Triceps Exercises:**
• Close Grip Bench: 4x8-10
• Tricep Pushdowns: 3x12-15
• Overhead Extensions: 3x10-12
• Dips: 3x10-15

**Focus:** Back thickness and triceps development.
""")
        
        # Individual muscle groups
        elif 'chest' in user_message:
            await update.message.reply_text("""
💪 **Chest Development Program**

**Strength Focus:**
• Barbell Bench Press: 4x6-8
• Incline Bench: 3x8-10
• Weighted Dips: 3x8-12

**Hypertrophy Focus:**
• Dumbbell Press: 4x10-12
• Incline Flyes: 3x12-15
• Cable Crossovers: 3x15-20
• Push-ups: 3x failure

**Pro Tips:** Vary grip widths, focus on mind-muscle connection.
""")
        
        elif 'back' in user_message:
            await update.message.reply_text("""
💪 **Back Development Program**

**Width (Lats):**
• Pull-ups: 4x6-12
• Lat Pulldowns: 3x10-12
• Straight Arm Pulldowns: 3x12-15

**Thickness (Rhomboids):**
• Barbell Rows: 4x8-10
• T-Bar Rows: 3x10-12
• Seated Cable Rows: 3x10-12

**Rear Delts:**
• Face Pulls: 3x15-20
• Rear Delt Flyes: 3x12-15
""")
        
        elif 'shoulder' in user_message:
            await update.message.reply_text("""
💪 **Shoulder Development Program**

**Front Delts:**
• Overhead Press: 4x6-10
• Front Raises: 3x12-15

**Side Delts:**
• Lateral Raises: 4x12-15
• Upright Rows: 3x10-12

**Rear Delts:**
• Rear Delt Flyes: 3x15-20
• Face Pulls: 3x15-20

**Important:** Light weight, perfect form for raises.
""")
        
        elif 'leg' in user_message:
            await update.message.reply_text("""
🦵 **Leg Development Program**

**Quads:**
• Barbell Squats: 4x6-10
• Leg Press: 3x10-15
• Lunges: 3x10-12 per leg

**Hamstrings:**
• Deadlifts: 3x6-8
• Leg Curls: 3x12-15
• Romanian Deadlifts: 3x10-12

**Calves:**
• Standing Calf Raises: 4x15-20
• Seated Calf Raises: 3x15-20

**Don't skip leg day!**
""")
        
        elif 'bicep' in user_message:
            await update.message.reply_text("""
💪 **Biceps Specialization**

**Mass Building:**
• Barbell Curls: 4x8-12
• Incline Dumbbell Curls: 3x10-12
• Hammer Curls: 3x10-12

**Peak Development:**
• Preacher Curls: 3x10-12
• Concentration Curls: 3x12-15

**Tips:** Control the negative, squeeze at the top.
""")
        
        elif 'tricep' in user_message:
            await update.message.reply_text("""
💪 **Triceps Specialization**

**Mass Building:**
• Close Grip Bench: 4x8-10
• Weighted Dips: 3x8-12
• Skull Crushers: 3x10-12

**Definition:**
• Tricep Pushdowns: 3x12-15
• Overhead Extensions: 3x10-12
• Kickbacks: 3x12-15
""")

    # === NUTRITION & DIET ===
    elif any(word in user_message for word in ['diet', 'nutrition', 'eat', 'food', 'meal']):
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
        
        elif 'pre workout' in user_message:
            await update.message.reply_text("""
⚡ **Pre-Workout Nutrition**

**1-2 Hours Before:**
• Complex carbs + protein
• Examples: Oatmeal + protein powder, Chicken + rice, Banana + peanut butter

**30-60 Minutes Before:**
• Simple carbs for energy
• Examples: Banana, Rice cakes, Sports drink

**Supplements:**
• Caffeine: 200-400mg for energy
• Creatine: 5g daily
• Beta-Alanine: for endurance

**Avoid:** Heavy, fatty meals right before training.
""")
        
        elif 'after workout' in user_message or 'post workout' in user_message:
            await update.message.reply_text("""
🥗 **Post-Workout Nutrition (Anabolic Window)**

**Within 1-2 Hours After Training:**

**Protein Sources:**
• Whey protein shake: 25-40g
• Chicken breast: 150-200g
• Greek yogurt: 200g
• Eggs: 3-4 whole eggs

**Carb Sources:**
• White rice: 1 cup
• Sweet potato: medium
• Fruits: Banana, berries
• Oats: 1/2 cup

**Why it matters:** Repairs muscle, replenishes glycogen, speeds recovery.
""")
        
        elif 'gain muscle' in user_message or 'bulk' in user_message:
            await update.message.reply_text("""
💪 **Muscle Gain Nutrition Strategy**

**Calories:** Maintenance + 300-500
**Protein:** 1.8-2.2g per kg bodyweight
**Carbs:** 4-6g per kg bodyweight
**Fats:** 0.8-1g per kg bodyweight

**Meal Timing:**
• Protein every 3-4 hours
• Carbs around workouts
• Healthy fats with meals

**Foods to Focus On:** Lean meats, complex carbs, healthy fats, vegetables.
""")
        
        elif 'lose fat' in user_message or 'weight loss' in user_message:
            await update.message.reply_text("""
📉 **Fat Loss Nutrition Strategy**

**Calories:** Maintenance - 300-500
**Protein:** 2-2.5g per kg bodyweight (preserves muscle)
**Carbs:** 2-3g per kg bodyweight
**Fats:** 0.8-1g per kg bodyweight

**Key Principles:**
• High protein for satiety
• Fiber from vegetables
• Limit processed foods
• Stay hydrated

**Foods to Avoid:** Sugary drinks, processed snacks, fried foods.
""")
        
        else:
            await update.message.reply_text("""
🥗 **General Nutrition Guidelines**

**What to Eat:**
• Lean proteins (chicken, fish, eggs)
• Complex carbs (oats, rice, sweet potato)
• Healthy fats (avocado, nuts, olive oil)
• Vegetables (all colors)
• Fruits (berries, apples, bananas)

**What to Avoid:**
• Sugary drinks and snacks
• Processed foods
• Trans fats
• Excessive alcohol

**Hydration:** 3-4 liters water daily.
""")

    # === GENERAL FITNESS ===
    elif any(word in user_message for word in ['water', 'hydrate', 'drink']):
        await update.message.reply_text("""
💧 **Hydration Guidelines**

**Daily Intake:** 3-4 liters (8-10 glasses)
**During Exercise:** 500ml-1 liter per hour
**Signs of Dehydration:** Dark urine, fatigue, headaches

**Benefits:**
• Improved performance
• Better recovery
• Joint health
• Temperature regulation

**Tips:** Drink throughout the day, not all at once.
""")
    
    elif 'cardio' in user_message:
        await update.message.reply_text("""
🏃 **Cardio Training Guidelines**

**For Fat Loss:**
• 3-5 sessions weekly
• 30-60 minutes per session
• Moderate intensity (can talk but not sing)

**For Health:**
• 150 mins moderate or 75 mins vigorous weekly
• Mix of steady-state and intervals

**Options:** Running, cycling, swimming, rowing, walking

**Timing:** Separate from strength training or after weights.
""")
    
    elif any(word in user_message for word in ['recovery', 'rest', 'sleep']):
        await update.message.reply_text("""
😴 **Recovery & Rest Guidelines**

**Sleep:** 7-9 hours quality sleep nightly
**Between Workouts:** 48 hours for same muscle group
**Active Recovery:** Light walking, stretching, yoga

**Recovery Techniques:**
• Foam rolling
• Stretching
• Massage
• Contrast showers (hot/cold)

**Signs of Overtraining:** Fatigue, poor performance, irritability, insomnia.
""")
    
    elif 'supplement' in user_message:
        await update.message.reply_text("""
💊 **Evidence-Based Supplements**

**Tier 1 (Most Beneficial):**
• **Protein Powder:** Convenient protein source
• **Creatine:** Strength and muscle gains
• **Omega-3 Fish Oil:** Joint and brain health

**Tier 2 (Conditional):**
• **Vitamin D:** If limited sun exposure
• **Multivitamin:** Nutrient insurance
• **Caffeine:** Pre-workout energy

**Tier 3 (Nice to Have):**
• **BCAAs:** During fasted training
• **Beta-Alanine:** Endurance support

**Remember:** Supplements supplement a good diet.
""")

    # === PERSONALIZED DIET INFO COLLECTION ===
    elif user_data[user_id].get("waiting_for_info", False):
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

    # === GREETINGS & DEFAULT ===
    elif any(word in user_message for word in ['hi', 'hello', 'hey']):
        await update.message.reply_text("👋 Hey! I'm your AI personal trainer. Ask me about workouts, nutrition, or fitness goals!")
    
    elif any(word in user_message for word in ['thank', 'thanks']):
        await update.message.reply_text("You're welcome! 💪 Keep crushing your fitness goals!")
    
    else:
        await update.message.reply_text("""
🤔 **How can I help you today?**

**Workout Programs:**
• Chest workout, Back & triceps, Push/pull/legs
• Shoulder specialization, Leg day routine

**Nutrition:**
• Diet plan, Pre-workout meals, Post-workout nutrition
• Muscle gain diet, Weight loss strategy

**General:**
• Hydration, Cardio, Recovery, Supplements

Ask me anything specific!
""")

async def generate_diet_plan(update: Update, diet_info):
    """Generate personalized diet plan based on user info"""
    age = diet_info.get('age', '30')
    weight = diet_info.get('weight', '75')
    height = diet_info.get('height', '180')
    activity = diet_info.get('activity', 'moderate')
    goal = diet_info.get('goal', 'muscle gain')
    
    plan = f"""
🥗 **Personalized Diet Plan**

**Based on your info:**
• Age: {age}
• Weight: {weight}kg
• Height: {height}cm
• Activity: {activity}
• Goal: {goal}

**Daily Targets:**
• Calories: {calculate_calories(weight, activity, goal)}
• Protein: {float(weight)*2}g
• Carbs: {float(weight)*3 if 'loss' in goal else float(weight)*4}g
• Fats: {float(weight)*0.8}g

**Sample Meal Plan:**
• Breakfast: Protein + complex carbs
• Lunch: Lean protein + vegetables + healthy fats
• Dinner: Similar to lunch, adjust carbs based on activity
• Snacks: Fruits, nuts, Greek yogurt

**Hydration:** 3-4 liters water daily
"""
    await update.message.reply_text(plan)

def calculate_calories(weight, activity, goal):
    base = float(weight) * 30
    if 'sedentary' in activity: base *= 1.2
    elif 'light' in activity: base *= 1.375
    elif 'moderate' in activity: base *= 1.55
    elif 'active' in activity: base *= 1.725
    else: base *= 1.9
    
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
            time.sleep(10)
            continue

if __name__ == '__main__':
    main()
