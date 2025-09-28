import os
import logging
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Detailed comprehensive responses
KNOWLEDGE = {
    "water": """
💧 **Water Intake Guidelines:**

**Daily Recommendation:** 3-4 liters (about 8-10 glasses)
**When to drink more:**
- During intense workouts
- In hot weather
- When sweating heavily
- If you feel thirsty

**Benefits of proper hydration:**
- Improves workout performance
- Aids muscle recovery
- Helps with fat loss
- Improves skin health
- Boosts energy levels

**Signs of dehydration:** Dark urine, fatigue, headaches, dry mouth
""",
    
    "post_workout": """
🥗 **Post-Workout Nutrition (Anabolic Window):**

**Timing:** Within 1-2 hours after training
**What to eat:** Protein + Fast-digesting carbs

**Ideal Options:**
- **Protein Shake** + Banana
- **Grilled Chicken** (150g) + Brown Rice (1 cup)
- **Greek Yogurt** + Berries + Honey
- **Eggs** (3-4) + Whole Wheat Toast
- **Tuna** + Sweet Potato

**Why this works:**
- Protein repairs muscle tissue
- Carbs replenish glycogen stores
- Speeds up recovery process
- Reduces muscle soreness
""",
    
    "protein": """
💪 **Protein Requirements for Fitness:**

**General Guidelines:**
- **Sedentary:** 0.8g per kg bodyweight
- **Exercising:** 1.2-1.6g per kg bodyweight
- **Strength Training:** 1.6-2.2g per kg bodyweight
- **Elite Athletes:** Up to 2.5g per kg bodyweight

**Example for 75kg person:** 120-165g protein daily

**Best Protein Sources:**
- **Animal:** Chicken, fish, eggs, Greek yogurt, lean beef
- **Plant:** Lentils, tofu, chickpeas, quinoa, nuts
- **Supplements:** Whey protein, casein, plant-based protein

**Distribution:** Spread throughout the day (20-40g per meal)
""",
    
    "sleep": """
😴 **Sleep & Recovery for Athletes:**

**Duration:** 7-9 hours quality sleep nightly

**Why sleep matters for fitness:**
- Muscle repair and growth happens during sleep
- Hormone production (testosterone, growth hormone)
- Mental recovery and focus
- Immune system support
- Energy restoration

**Tips for better sleep:**
- Consistent sleep schedule
- Dark, cool bedroom
- No screens 1 hour before bed
- Avoid caffeine after 2 PM
- Relaxation routine before sleep
""",
    
    "chest": """
💪 **Complete Chest Workout Routine:**

**Warm-up (5 minutes):**
- Arm circles: 1 minute
- Push-ups: 2 sets of 10 reps
- Dynamic stretching: 2 minutes

**Main Workout:**
1. **Barbell Bench Press:** 4 sets x 6-10 reps
   - Focus on chest contraction
   - 2-3 minutes rest between sets

2. **Incline Dumbbell Press:** 3 sets x 8-12 reps
   - Targets upper chest
   - Control the negative phase

3. **Cable Crossovers:** 3 sets x 12-15 reps
   - Peak contraction at center
   - Constant tension on chest

4. **Push-ups:** 3 sets to failure
   - Great finisher exercise
   - Focus on full range of motion

**Pro Tips:**
- Keep shoulders back and down
- Don't bounce the bar off your chest
- Squeeze chest at top of movement
- Progressive overload each week
""",
    
    "back": """
💪 **Complete Back Development Workout:**

**Warm-up:** Lat pulldowns (light weight) 2x15

**Main Workout:**
1. **Pull-ups/Chin-ups:** 4 sets x 6-12 reps
   - Builds width and strength
   - Use assistance if needed

2. **Bent-over Barbell Rows:** 4 sets x 8-10 reps
   - Thickness development
   - Keep back straight, pull to lower chest

3. **Seated Cable Rows:** 3 sets x 10-12 reps
   - Mid-back focus
   - Squeeze shoulder blades together

4. **Face Pulls:** 3 sets x 15-20 reps
   - Rear delts and rotator cuff health
   - External rotation at peak

**Form Tips:**
- Mind-muscle connection with back
- Don't use momentum
- Full range of motion
- Controlled negative phase
""",
    
    "legs": """
🦵 **Complete Leg Day Routine:**

**Warm-up:** 5 minutes dynamic stretching

**Quad Focus:**
1. **Barbell Squats:** 4 sets x 6-10 reps
   - Depth to parallel or below
   - Drive through heels

2. **Leg Press:** 3 sets x 10-15 reps
   - Controlled movement
   - Don't lock knees at top

**Hamstring Focus:**
3. **Romanian Deadlifts:** 3 sets x 8-12 reps
   - Feel stretch in hamstrings
   - Soft knees, hinge at hips

4. **Walking Lunges:** 3 sets x 10-12 reps per leg
   - Stability and balance
   - Controlled steps

**Accessory:**
5. **Calf Raises:** 4 sets x 15-20 reps
   - Full stretch and contraction

**Important:** Don't skip leg day! Leg training boosts overall muscle growth.
"""
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **FitCoach AI** - Your Detailed Fitness Guide\n\n"
        "Ask me about:\n"
        "• Specific workouts (chest, back, legs, etc.)\n"
        "• Nutrition timing and requirements\n"
        "• Recovery and supplementation\n"
        "• Exercise form and techniques"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.lower()
    
    if any(word in user_message for word in ['water', 'drink', 'hydrate', 'liter']):
        await update.message.reply_text(KNOWLEDGE["water"])
    
    elif any(word in user_message for word in ['after gym', 'after workout', 'post workout', 'eat after gym']):
        await update.message.reply_text(KNOWLEDGE["post_workout"])
    
    elif any(word in user_message for word in ['protein', 'how much protein', 'protein intake']):
        await update.message.reply_text(KNOWLEDGE["protein"])
    
    elif any(word in user_message for word in ['sleep', 'rest', 'recovery', 'how much sleep']):
        await update.message.reply_text(KNOWLEDGE["sleep"])
    
    elif 'chest' in user_message:
        await update.message.reply_text(KNOWLEDGE["chest"])
    elif 'back' in user_message:
        await update.message.reply_text(KNOWLEDGE["back"])
    elif 'leg' in user_message or 'squat' in user_message:
        await update.message.reply_text(KNOWLEDGE["legs"])
    elif 'bicep' in user_message:
        await update.message.reply_text("💪 **Biceps Workout:**\n\n• Barbell Curls: 4x8-12\n• Hammer Curls: 3x10-12\n• Concentration Curls: 3x12-15\n• Focus on squeeze and controlled negatives")
    elif 'tricep' in user_message:
        await update.message.reply_text("💪 **Triceps Workout:**\n\n• Close Grip Bench: 4x8-10\n• Tricep Pushdowns: 3x12-15\n• Overhead Extensions: 3x10-12\n• Dips: 3x10-15\n• Keep elbows tucked for maximum triceps engagement")
    elif 'shoulder' in user_message:
        await update.message.reply_text("💪 **Shoulders Workout:**\n\n• Overhead Press: 4x6-10\n• Lateral Raises: 4x12-15\n• Front Raises: 3x12-15\n• Rear Delt Flyes: 3x15-20\n• Focus on light weight and perfect form for raises")
    
    elif 'weight loss' in user_message:
        await update.message.reply_text("""
📉 **Weight Loss Strategy:**

**Nutrition:**
- Calorie deficit (maintenance - 300-500 calories)
- High protein intake (2g per kg bodyweight)
- Fiber-rich vegetables with every meal
- Limit processed foods and sugars
- Stay hydrated (water before meals)

**Training:**
- Strength training 3-4x weekly
- Cardio 2-3x weekly (HIIT or steady state)
- Daily activity (walking, steps)

**Key Principle:** Consistency over perfection
""")
    
    elif 'muscle gain' in user_message:
        await update.message.reply_text("""
💪 **Muscle Gain Strategy:**

**Nutrition:**
- Calorie surplus (maintenance + 300-500 calories)
- Protein: 1.8-2.2g per kg bodyweight
- Carbs around workouts for energy
- Healthy fats for hormone production
- Meal frequency: 4-6 meals daily

**Training:**
- Progressive overload (increase weight/reps weekly)
- Compound movements focus
- 48 hours recovery between muscle groups
- 7-9 hours sleep nightly

**Supplements:** Protein powder, creatine, omega-3s
""")
    
    elif 'hi' in user_message or 'hello' in user_message:
        await update.message.reply_text("👋 Hello! I'm your detailed fitness coach. Ask me anything about workouts, nutrition, or recovery!")
    
    else:
        await update.message.reply_text("💪 Ask me about specific workouts, nutrition timing, recovery strategies, or exercise techniques!")

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
