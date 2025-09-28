import os
import logging
import time
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ... (keep the previous imports and setup)

# Enhanced workout combinations mapping with more keywords
WORKOUT_COMBINATIONS = {
    # Single muscle groups
    'chest': ['chest', 'pec', 'pectoral', 'bench'],
    'back': ['back', 'lats', 'latissimus', 'row', 'pullup', 'pull-up', 'pull up'],
    'shoulders': ['shoulder', 'delts', 'deltoid', 'press', 'overhead'],
    'biceps': ['bicep', 'curl', 'bicep'],
    'triceps': ['tricep', 'pushdown', 'extension'],
    'legs': ['leg', 'quad', 'hamstring', 'glute', 'calf', 'squat', 'deadlift'],
    'core': ['core', 'ab', 'abdominal', 'plank', 'crunch'],
    
    # Common combinations
    'chest_biceps': ['chest and bicep', 'chest bicep', 'chest & bicep'],
    'back_triceps': ['back and tricep', 'back tricep', 'back & tricep'],
    'shoulders_arms': ['shoulder and arm', 'shoulder arm', 'shoulders arms'],
    'push': ['push day', 'push workout', 'chest shoulder tricep'],
    'pull': ['pull day', 'pull workout', 'back bicep'],
    'legs_core': ['leg and core', 'leg core', 'lower body'],
    'upper_body': ['upper body', 'upper day', 'upper workout'],
    'full_body': ['full body', 'total body', 'all muscle']
}

# Exercise tips database
EXERCISE_TIPS = {
    'squat': """
🏋️ **SQUAT - Proper Form Tips**

**Setup:**
• Feet shoulder-width apart, toes slightly out
• Bar across upper back (not neck)
• Chest up, back straight

**Execution:**
• Break at hips first, then knees
• Descend until thighs parallel to floor
• Keep knees tracking over toes
• Drive through heels to stand

**Common Mistakes:**
❌ Knees caving in
❌ Rounding lower back
❌ Heels lifting off ground
❌ Not reaching depth

**Pro Tips:**
• Brace core like you're about to be punched
• Look straight ahead, not up or down
• Control the descent, explode upward
""",

    'deadlift': """
🏋️ **DEADLIFT - Proper Form Tips**

**Setup:**
• Feet hip-width, bar over mid-foot
• Bend hips and knees to grip bar
• Hands just outside legs
• Chest up, back flat

**Execution:**
• Drive through heels
• Keep bar close to body (shaves legs)
• Stand up fully, squeeze glutes
• Lower under control

**Common Mistakes:**
❌ Rounding the back
❌ Bar drifting away from body
❌ Hips shooting up first
❌ Not engaging lats

**Variations:**
• Conventional: Mixed grip for heavy weights
• Sumo: Wider stance, more quad focus
• Romanian: Hamstring and glute focus
""",

    'bench': """
🏋️ **BENCH PRESS - Proper Form Tips**

**Setup:**
• Lie with eyes under bar
• Feet firmly on floor
• Arch back slightly
• Shoulder blades retracted

**Grip & Execution:**
• Grip slightly wider than shoulders
• Lower bar to lower chest/mid-sternum
• Keep elbows at 45-60 degree angle
• Drive feet into floor for leg drive

**Common Mistakes:**
❌ Flaring elbows at 90 degrees
❌ Bouncing bar off chest
❌ Lifting hips off bench
❌ Not full range of motion

**Safety:**
• Use spotter for heavy weights
• Learn roll of shame for failure
• Warm up shoulders properly
""",

    'pullup': """
🏋️ **PULL-UP - Proper Form Tips**

**Setup:**
• Grip slightly wider than shoulders
• Palms facing away (chin-up: palms facing)
• Hang with arms fully extended

**Execution:**
• Pull shoulder blades down first
• Drive elbows toward hips
• Chin over bar at top
• Lower under control

**Common Mistakes:**
❌ Using momentum (kipping)
❌ Not reaching full extension
❌ Shrugging shoulders at top
❌ Partial range of motion

**Progressions:**
• Negative pull-ups (jump up, slow down)
• Band-assisted pull-ups
• Lat pulldown machine
• Inverted rows
"""
}

# Nutrition plans
NUTRITION_PLANS = {
    'general': """
🥗 **General Nutrition Guidelines**

**Macronutrient Breakdown:**
• Protein: 1.6-2.2g per kg body weight
• Carbs: 3-5g per kg body weight  
• Fats: 0.8-1g per kg body weight

**Meal Timing:**
• 3-5 meals spaced throughout day
• Protein with every meal
• Carbs around workouts
• Post-workout: Protein + carbs within 2 hours

**Food Quality:**
✅ **Eat More:** Lean meats, fish, eggs, vegetables, fruits, whole grains
❌ **Eat Less:** Processed foods, sugary drinks, trans fats

**Hydration:** 3-4 liters water daily
""",

    'weight loss': """
📉 **Weight Loss Nutrition Plan**

**Calorie Deficit:** Maintenance - 300-500 calories
**Protein:** 2-2.5g per kg body weight (preserves muscle)

**Daily Targets (example 75kg person):**
• Calories: ~2000-2200
• Protein: 150-180g
• Carbs: 150-200g
• Fats: 50-60g

**Strategies:**
• High protein for satiety
• Fiber from vegetables
• Limit processed carbs
• Healthy fats for hormones

**Food Focus:**
• Lean proteins: Chicken, fish, Greek yogurt
• Vegetables: Broccoli, spinach, peppers
• Healthy fats: Avocado, nuts, olive oil
• Complex carbs: Oats, sweet potato, quinoa
""",

    'muscle gain': """
💪 **Muscle Gain Nutrition Plan**

**Calorie Surplus:** Maintenance + 300-500 calories
**Protein:** 1.8-2.2g per kg body weight

**Daily Targets (example 75kg person):**
• Calories: ~2800-3200
• Protein: 135-165g
• Carbs: 350-450g
• Fats: 60-80g

**Strategies:**
• Consistent calorie surplus
• Protein every 3-4 hours
• Carbs around workouts
• Don't fear healthy fats

**Food Focus:**
• Protein: Chicken, beef, eggs, protein powder
• Carbs: Rice, pasta, potatoes, oats
• Fats: Nuts, seeds, avocado, olive oil
• Calorie-dense: Nut butters, dried fruits
"""
}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages with comprehensive coverage"""
    try:
        user_message = update.message.text.lower()
        user_id = update.message.from_user.id
        
        # Store conversation context
        if user_id not in user_data:
            user_data[user_id] = {"diet_info": {}}

        # === EXERCISE TIPS ===
        for exercise, tips in EXERCISE_TIPS.items():
            if exercise in user_message:
                await update.message.reply_text(tips)
                return

        # === NUTRITION PLANS ===
        if 'nutrition' in user_message or 'diet' in user_message:
            if 'weight loss' in user_message or 'lose weight' in user_message:
                await update.message.reply_text(NUTRITION_PLANS['weight loss'])
                return
            elif 'muscle gain' in user_message or 'bulk' in user_message or 'gain muscle' in user_message:
                await update.message.reply_text(NUTRITION_PLANS['muscle gain'])
                return
            elif 'general' in user_message or 'basic' in user_message:
                await update.message.reply_text(NUTRITION_PLANS['general'])
                return

        # === PERSONALIZED DIET PLAN ===
        if 'diet plan' in user_message:
            user_data[user_id]["waiting_for_info"] = True
            await update.message.reply_text("""
🎯 **Personalized Diet Plan Creator**

I'll create a custom nutrition plan for you! I need:

1. **Age:** 
2. **Weight (kg):** 
3. **Height (cm):** 
4. **Activity Level** (sedentary/light/moderate/active/very active):
5. **Goal** (weight loss/muscle gain/maintenance):

**Example:** "I'm 25, 75kg, 180cm, moderate activity, want muscle gain"

Tell me your details!
""")
            return

        # === SINGLE MUSCLE GROUP WORKOUTS ===
        muscle_workouts = {
            'chest': """
💪 **CHEST WORKOUT**

**Compound Movements:**
• Bench Press: 4x6-12
• Incline Dumbbell Press: 3x8-12
• Decline Bench Press: 3x8-12

**Isolation & Accessories:**
• Cable Fly: 3x12-15
• Pec Deck: 3x12-15
• Push-ups: 3x15-20

**Tips:** 
• Vary grip widths for complete development
• Focus on mind-muscle connection
• Don't neglect upper and lower chest
""",

            'back': """
💪 **BACK WORKOUT**

**Width Exercises (Lats):**
• Pull-ups: 4x6-12
• Lat Pulldown: 3x10-12
• Straight Arm Pulldown: 3x12-15

**Thickness Exercises:**
• Barbell Row: 4x8-10
• T-Bar Row: 3x8-12
• Seated Cable Row: 3x10-12

**Rear Delts:**
• Face Pulls: 3x15-20
• Rear Delt Fly: 3x12-15

**Focus:** Squeeze shoulder blades together
""",

            'shoulders': """
💪 **SHOULDER WORKOUT**

**Front Delts:**
• Overhead Press: 4x6-10
• Front Raises: 3x12-15

**Side Delts (Width):**
• Lateral Raises: 4x12-15
• Upright Rows: 3x10-12

**Rear Delts:**
• Rear Delt Fly: 3x15-20
• Face Pulls: 3x15-20

**Important:** 
• Light weight, perfect form for raises
• Don't neglect rear delts for balanced development
""",

            'biceps': """
💪 **BICEPS WORKOUT**

**Mass Building:**
• Barbell Curls: 4x8-12
• Incline Dumbbell Curls: 3x10-12
• Hammer Curls: 3x10-12

**Peak & Definition:**
• Preacher Curls: 3x10-12
• Concentration Curls: 3x12-15
• Cable Curls: 3x12-15

**Tips:**
• Control the negative (lower slowly)
• Squeeze at the top
• Don't use momentum
""",

            'triceps': """
💪 **TRICEPS WORKOUT**

**Mass Building:**
• Close Grip Bench: 4x8-10
• Weighted Dips: 3x8-12
• Skull Crushers: 3x10-12

**Definition & Shape:**
• Tricep Pushdown: 3x12-15
• Overhead Extension: 3x10-12
• Kickbacks: 3x12-15

**Anatomy:** 
• Long head: Overhead movements
• Lateral head: Pushdowns
• Medial head: All compound movements
""",

            'legs': """
🦵 **LEGS WORKOUT**

**Quads Focus:**
• Barbell Squats: 4x6-10
• Leg Press: 3x10-15
• Lunges: 3x10-12 per leg

**Hamstrings & Glutes:**
• Deadlifts: 3x6-8
• Leg Curls: 3x12-15
• Romanian Deadlifts: 3x10-12

**Calves:**
• Standing Calf Raises: 4x15-20
• Seated Calf Raises: 3x15-20

**Don't skip leg day!** Balanced physique requires strong legs.
"""
        }

        # Check for single muscle group requests
        for muscle, workout in muscle_workouts.items():
            if muscle in user_message:
                await update.message.reply_text(workout)
                return

        # === WORKOUT COMBINATIONS ===
        workout_type, workout_category = detect_workout_type(user_message)
        
        if workout_type:
            workout_response = await generate_workout_response(workout_type, workout_category)
            if workout_response:
                await update.message.reply_text(workout_response)
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
            await update.message_reply_text("""
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
            await update.message.reply_text("""
👋 **Welcome to Your AI Personal Trainer!**

I can help you with:

💪 **Workouts:** chest, back, biceps, triceps, shoulders, legs
🥗 **Nutrition:** general, weight loss, muscle gain  
🎯 **Personalized Diet Plan:** Type 'diet plan'
🏋️ **Exercise Tips:** squat, deadlift, bench, pullup

Just tell me what you need! 💪
""")
            return

        elif any(word in user_message for word in ['thank', 'thanks']):
            await update.message.reply_text("You're welcome! 💪 Keep crushing your fitness goals!")
            return

        else:
            await update.message.reply_text("""
🤔 **How can I help you today?**

💪 **Workouts:** 
• "chest workout", "back exercises", "shoulder day"
• "biceps routine", "triceps training", "leg day"
• "push workout", "pull day", "full body"

🥗 **Nutrition:**
• "general nutrition", "weight loss diet", "muscle gain nutrition"
• "diet plan" (personalized)

🏋️ **Exercise Tips:**
• "squat form", "deadlift tips", "bench press", "pullup technique"

Just ask! I'm here to help 💪
""")
            
    except Exception as e:
        logger.error(f"Error in handle_message: {e}")
        try:
            await update.message.reply_text("❌ Sorry, I encountered an error. Please try again.")
        except:
            pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
🏋️ **Your AI Personal Trainer**

I can help you with:

💪 **Workouts:** 
• Chest, Back, Biceps, Triceps, Shoulders, Legs
• Push/Pull/Legs, Upper/Lower, Full Body

🥗 **Nutrition:**
• General guidelines
• Weight loss plans  
• Muscle gain strategies
• Personalized diet plans

🏋️ **Exercise Tips:**
• Squat, Deadlift, Bench Press, Pull-up form

🎯 **Just ask naturally:**
• "chest workout"
• "weight loss nutrition" 
• "squat tips"
• "diet plan"

Let's get started! 💪
""")

# ... (keep the generate_diet_plan, calculate_calories, and other functions the same)
