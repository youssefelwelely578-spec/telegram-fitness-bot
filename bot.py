import os
import logging
import time
import asyncio
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ... (keep the previous imports and setup)

# Enhanced workout combinations mapping
WORKOUT_COMBINATIONS = {
    # Single muscle groups
    'chest': ['chest', 'pec', 'pectoral', 'bench'],
    'back': ['back', 'lats', 'latissimus', 'row', 'pullup', 'pull-up'],
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

# Enhanced exercise database with more variations
EXERCISE_DATABASE = {
    "chest": [
        {"name": "Bench Press", "type": "Compound", "equipment": "Barbell/Bench", "sets_reps": "4x6-12"},
        {"name": "Incline Dumbbell Press", "type": "Compound", "equipment": "Dumbbells/Bench", "sets_reps": "3x8-12"},
        {"name": "Cable Fly", "type": "Isolation", "equipment": "Cable Machine", "sets_reps": "3x12-15"},
        {"name": "Push-ups", "type": "Compound", "equipment": "Bodyweight", "sets_reps": "3x15-20"},
        {"name": "Pec Deck", "type": "Isolation", "equipment": "Machine", "sets_reps": "3x12-15"},
        {"name": "Decline Bench Press", "type": "Compound", "equipment": "Barbell/Bench", "sets_reps": "3x8-12"}
    ],
    "back": [
        {"name": "Pull-ups", "type": "Compound", "equipment": "Bodyweight/Bar", "sets_reps": "4x6-12"},
        {"name": "Barbell Row", "type": "Compound", "equipment": "Barbell", "sets_reps": "4x8-10"},
        {"name": "Lat Pulldown", "type": "Compound", "equipment": "Cable Machine", "sets_reps": "3x10-12"},
        {"name": "Seated Cable Row", "type": "Compound", "equipment": "Cable Machine", "sets_reps": "3x10-12"},
        {"name": "Face Pulls", "type": "Isolation", "equipment": "Cable Machine", "sets_reps": "3x15-20"},
        {"name": "T-Bar Row", "type": "Compound", "equipment": "Machine/Barbell", "sets_reps": "3x8-12"}
    ],
    "shoulders": [
        {"name": "Overhead Press", "type": "Compound", "equipment": "Barbell/Dumbbells", "sets_reps": "4x6-10"},
        {"name": "Lateral Raise", "type": "Isolation", "equipment": "Dumbbells", "sets_reps": "3x12-15"},
        {"name": "Front Raise", "type": "Isolation", "equipment": "Dumbbells", "sets_reps": "3x12-15"},
        {"name": "Rear Delt Fly", "type": "Isolation", "equipment": "Dumbbells", "sets_reps": "3x15-20"},
        {"name": "Upright Row", "type": "Compound", "equipment": "Barbell/Dumbbells", "sets_reps": "3x10-12"},
        {"name": "Shrugs", "type": "Isolation", "equipment": "Barbell/Dumbbells", "sets_reps": "3x12-15"}
    ],
    "biceps": [
        {"name": "Barbell Curl", "type": "Isolation", "equipment": "Barbell", "sets_reps": "4x8-12"},
        {"name": "Dumbbell Curl", "type": "Isolation", "equipment": "Dumbbells", "sets_reps": "3x10-12"},
        {"name": "Hammer Curl", "type": "Isolation", "equipment": "Dumbbells", "sets_reps": "3x10-12"},
        {"name": "Preacher Curl", "type": "Isolation", "equipment": "Bench/Barbell", "sets_reps": "3x10-12"},
        {"name": "Concentration Curl", "type": "Isolation", "equipment": "Dumbbell", "sets_reps": "3x12-15"},
        {"name": "Cable Curl", "type": "Isolation", "equipment": "Cable Machine", "sets_reps": "3x12-15"}
    ],
    "triceps": [
        {"name": "Tricep Pushdown", "type": "Isolation", "equipment": "Cable Machine", "sets_reps": "3x12-15"},
        {"name": "Overhead Extension", "type": "Isolation", "equipment": "Dumbbell/Cable", "sets_reps": "3x10-12"},
        {"name": "Close Grip Bench", "type": "Compound", "equipment": "Barbell", "sets_reps": "4x8-10"},
        {"name": "Dips", "type": "Compound", "equipment": "Bodyweight", "sets_reps": "3x10-15"},
        {"name": "Skull Crushers", "type": "Isolation", "equipment": "Barbell/Dumbbells", "sets_reps": "3x10-12"},
        {"name": "Tricep Kickback", "type": "Isolation", "equipment": "Dumbbell", "sets_reps": "3x12-15"}
    ],
    "legs": [
        {"name": "Squats", "type": "Compound", "equipment": "Barbell", "sets_reps": "4x6-10"},
        {"name": "Deadlift", "type": "Compound", "equipment": "Barbell", "sets_reps": "3x6-8"},
        {"name": "Leg Press", "type": "Compound", "equipment": "Machine", "sets_reps": "3x10-15"},
        {"name": "Lunges", "type": "Compound", "equipment": "Dumbbells/Barbell", "sets_reps": "3x10-12"},
        {"name": "Leg Curl", "type": "Isolation", "equipment": "Machine", "sets_reps": "3x12-15"},
        {"name": "Leg Extension", "type": "Isolation", "equipment": "Machine", "sets_reps": "3x12-15"},
        {"name": "Calf Raises", "type": "Isolation", "equipment": "Machine/Bodyweight", "sets_reps": "4x15-20"}
    ],
    "core": [
        {"name": "Plank", "type": "Bodyweight", "equipment": "None", "sets_reps": "3x60sec"},
        {"name": "Hanging Leg Raise", "type": "Isolation", "equipment": "Pull-up Bar", "sets_reps": "3x12-15"},
        {"name": "Russian Twists", "type": "Isolation", "equipment": "Bodyweight/Dumbbell", "sets_reps": "3x15-20"},
        {"name": "Cable Crunch", "type": "Isolation", "equipment": "Cable Machine", "sets_reps": "3x15-20"},
        {"name": "Leg Raises", "type": "Isolation", "equipment": "Floor/Bench", "sets_reps": "3x15-20"}
    ]
}

# Pre-built workout combinations
WORKOUT_PLANS = {
    'chest_biceps': {
        'name': 'Chest & Biceps',
        'description': 'Perfect combination for upper body push and arm development',
        'exercises': {
            'chest': ['Bench Press', 'Incline Dumbbell Press', 'Cable Fly'],
            'biceps': ['Barbell Curl', 'Hammer Curl', 'Concentration Curl']
        }
    },
    'back_triceps': {
        'name': 'Back & Triceps',
        'description': 'Great for back thickness and arm strength',
        'exercises': {
            'back': ['Pull-ups', 'Barbell Row', 'Lat Pulldown'],
            'triceps': ['Close Grip Bench', 'Tricep Pushdown', 'Overhead Extension']
        }
    },
    'shoulders_arms': {
        'name': 'Shoulders & Arms',
        'description': 'Complete shoulder and arm development',
        'exercises': {
            'shoulders': ['Overhead Press', 'Lateral Raise', 'Rear Delt Fly'],
            'biceps': ['Dumbbell Curl', 'Preacher Curl'],
            'triceps': ['Tricep Pushdown', 'Skull Crushers']
        }
    },
    'push': {
        'name': 'Push Day',
        'description': 'Chest, Shoulders, and Triceps focus',
        'exercises': {
            'chest': ['Bench Press', 'Incline Dumbbell Press'],
            'shoulders': ['Overhead Press', 'Lateral Raise'],
            'triceps': ['Close Grip Bench', 'Tricep Pushdown']
        }
    },
    'pull': {
        'name': 'Pull Day',
        'description': 'Back and Biceps focus',
        'exercises': {
            'back': ['Pull-ups', 'Barbell Row', 'Face Pulls'],
            'biceps': ['Barbell Curl', 'Hammer Curl']
        }
    },
    'legs_core': {
        'name': 'Legs & Core',
        'description': 'Complete lower body and core workout',
        'exercises': {
            'legs': ['Squats', 'Deadlift', 'Leg Press', 'Leg Curl'],
            'core': ['Plank', 'Hanging Leg Raise', 'Russian Twists']
        }
    },
    'upper_body': {
        'name': 'Upper Body',
        'description': 'Complete upper body workout',
        'exercises': {
            'chest': ['Bench Press', 'Incline Press'],
            'back': ['Pull-ups', 'Seated Row'],
            'shoulders': ['Overhead Press', 'Lateral Raise'],
            'biceps': ['Barbell Curl'],
            'triceps': ['Tricep Pushdown']
        }
    },
    'full_body': {
        'name': 'Full Body',
        'description': 'Complete body workout hitting all major muscle groups',
        'exercises': {
            'chest': ['Bench Press'],
            'back': ['Pull-ups'],
            'shoulders': ['Overhead Press'],
            'legs': ['Squats'],
            'biceps': ['Dumbbell Curl'],
            'triceps': ['Tricep Pushdown'],
            'core': ['Plank']
        }
    }
}

def detect_workout_type(user_message):
    """Detect what type of workout the user is asking for"""
    user_message = user_message.lower()
    
    detected_workouts = []
    
    # Check for specific combinations first
    for combo, keywords in WORKOUT_COMBINATIONS.items():
        if any(keyword in user_message for keyword in keywords):
            detected_workouts.append(combo)
    
    # Remove duplicates and prioritize combinations
    unique_workouts = list(set(detected_workouts))
    
    # If multiple single muscle groups detected, create custom combo
    single_muscles = [w for w in unique_workouts if w in ['chest', 'back', 'shoulders', 'biceps', 'triceps', 'legs', 'core']]
    
    if len(single_muscles) >= 2:
        combo_name = '_'.join(single_muscles)
        return combo_name, 'custom'
    elif len(unique_workouts) == 1:
        return unique_workouts[0], 'prebuilt'
    elif 'workout' in user_message or 'exercise' in user_message:
        return 'full_body', 'prebuilt'
    else:
        return None, None

async def generate_workout_response(workout_type, workout_category):
    """Generate workout response based on detected type"""
    if workout_category == 'prebuilt' and workout_type in WORKOUT_PLANS:
        plan = WORKOUT_PLANS[workout_type]
        response = f"💪 **{plan['name']} Workout**\n\n"
        response += f"*{plan['description']}*\n\n"
        
        for muscle_group, exercises in plan['exercises'].items():
            response += f"**{muscle_group.title()}:**\n"
            for exercise in exercises:
                # Find exercise details
                for db_exercise in EXERCISE_DATABASE.get(muscle_group, []):
                    if db_exercise['name'] == exercise:
                        response += f"• {exercise}: {db_exercise['sets_reps']}\n"
                        break
            response += "\n"
        
        response += "**Tips:** Focus on proper form, control the negative, and push through the sticking point!"
        return response
    
    elif workout_category == 'custom':
        muscles = workout_type.split('_')
        response = f"💪 **Custom {' & '.join(muscle.title() for muscle in muscles)} Workout**\n\n"
        
        for muscle in muscles:
            if muscle in EXERCISE_DATABASE:
                response += f"**{muscle.title()} Exercises:**\n"
                # Show 3-4 exercises per muscle group
                for exercise in EXERCISE_DATABASE[muscle][:4]:
                    response += f"• {exercise['name']}: {exercise['sets_reps']}\n"
                response += "\n"
        
        response += "**Workout Structure:**\n"
        response += "• Warm-up: 5-10 minutes dynamic stretching\n"
        response += "• Main exercises: 3-4 sets each\n"
        response += "• Cool down: 5 minutes stretching\n\n"
        response += "**Rest:** 60-90 seconds between sets"
        return response
    
    else:
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages with improved workout detection"""
    try:
        user_message = update.message.text.lower()
        user_id = update.message.from_user.id
        
        # Store conversation context
        if user_id not in user_data:
            user_data[user_id] = {"diet_info": {}}
        
        # === IMPROVED WORKOUT DETECTION ===
        workout_type, workout_category = detect_workout_type(user_message)
        
        if workout_type:
            workout_response = await generate_workout_response(workout_type, workout_category)
            if workout_response:
                await update.message.reply_text(workout_response)
                return
            else:
                # Fallback to individual muscle group
                for muscle_group in ['chest', 'back', 'shoulders', 'biceps', 'triceps', 'legs', 'core']:
                    if muscle_group in user_message:
                        response = f"💪 **{muscle_group.title()} Exercises**\n\n"
                        for exercise in EXERCISE_DATABASE[muscle_group]:
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
• "shoulder workout", "leg day", "chest and biceps"
• "push workout", "pull day", "back and triceps" 
• "full body", "upper body", "arms workout"

**Nutrition & Diet:**
• "diet plan", "nutrition guidelines", "macros"
• "supplements", "hydration"

**General Fitness:**
• "anatomy", "muscle groups"
• "cardio", "recovery", "mindset"

Just tell me what workout you want to do!
""")
            
    except Exception as e:
        logger.error(f"Error in handle_message: {e}")
        try:
            await update.message.reply_text("❌ Sorry, I encountered an error processing your request. Please try again.")
        except:
            pass

# ... (keep the rest of the functions like generate_diet_plan, calculate_calories, etc.)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏋️ **Your AI Personal Trainer**\n\n"
        "I can help you with:\n"
        "• Complete workout programs & training splits\n"
        "• Exercise database with 100+ exercises\n"
        "• Personalized diet & nutrition plans\n"
        "• Muscle anatomy & exercise form\n"
        "• Recovery, hydration & supplements\n\n"
        "**Just ask naturally like:**\n"
        "• 'I want a shoulder workout'\n"
        "• 'Give me chest and biceps exercises'\n"
        "• 'Leg day routine'\n"
        "• 'Push workout please'\n"
        "• 'Back and triceps training'\n\n"
        "I understand natural language - just tell me what you want! 💪"
    )

# ... (keep the main function and bot manager the same)
