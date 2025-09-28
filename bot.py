import os
import logging
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Knowledge base
KNOWLEDGE = {
    "water": "💧 **Water Intake Guidelines:**\n\nDaily: 3-4 liters\nHydrate more during workouts or heat\nBenefits: performance, recovery, fat loss",
    "post_workout": "🥗 **Post-Workout Nutrition:**\nProtein + fast carbs within 1-2h\nExamples: Protein shake + banana, chicken + rice, Greek yogurt + berries",
    "protein": "💪 **Protein Requirements:**\nExercising: 1.2-2.2g/kg\nSources: chicken, fish, eggs, lentils, tofu, whey\nSpread throughout the day",
    "sleep": "😴 **Sleep & Recovery:**\n7-9 hours/night\nMuscle repair, hormone production, focus, immunity\nTips: dark room, consistent schedule, no screens before bed",
    "chest": "💪 **Chest Workout:**\nBench Press, Incline Dumbbell Press, Cable Crossovers, Push-ups\nFocus: form, squeeze, progressive overload",
    "back": "💪 **Back Workout:**\nPull-ups, Barbell Rows, Seated Cable Rows, Face Pulls\nFocus: mind-muscle connection, controlled movement",
    "legs": "🦵 **Leg Workout:**\nSquats, Leg Press, Romanian Deadlifts, Walking Lunges, Calf Raises\nWarm-up & full range of motion",
    "biceps": "💪 **Biceps Workout:**\nBarbell Curls, Hammer Curls, Concentration Curls\nSqueeze, controlled negatives",
    "triceps": "💪 **Triceps Workout:**\nClose Grip Bench, Pushdowns, Overhead Extensions, Dips\nElbows tucked for max engagement",
    "shoulders": "💪 **Shoulders Workout:**\nOverhead Press, Lateral/Front Raises, Rear Delt Flyes\nLight weight, perfect form",
    "push_pull_legs": "🔥 **Push/Pull/Legs Split:**\nPush: chest, shoulders, triceps\nPull: back, biceps\nLegs: quads, hamstrings, calves\nAlternate 6x/week",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **FitCoach AI** - Your Personal Trainer\n\n"
        "Ask me about workouts (chest, back, legs, biceps, triceps, shoulders), nutrition, recovery, supplements, and personalized diet tips!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.lower()

    # Check for workout keywords
    if any(w in msg for w in ["chest", "back", "leg", "squat", "bicep", "tricep", "shoulder"]):
        responses = []
        if "chest" in msg:
            responses.append(KNOWLEDGE["chest"])
        if "back" in msg:
            responses.append(KNOWLEDGE["back"])
        if "leg" in msg or "squat" in msg:
            responses.append(KNOWLEDGE["legs"])
        if "bicep" in msg:
            responses.append(KNOWLEDGE["biceps"])
        if "tricep" in msg:
            responses.append(KNOWLEDGE["triceps"])
        if "shoulder" in msg:
            responses.append(KNOWLEDGE["shoulders"])
        await update.message.reply_text("\n\n".join(responses))
        return

    # Push/pull/legs
    if "push pull legs" in msg:
        await update.message.reply_text(KNOWLEDGE["push_pull_legs"])
        return

    # Nutrition & hydration
    if any(w in msg for w in ["water", "drink", "hydrate"]):
        await update.message.reply_text(KNOWLEDGE["water"])
        return
    if any(w in msg for w in ["protein", "protein intake"]):
        await update.message.reply_text(KNOWLEDGE["protein"])
        return
    if any(w in msg for w in ["sleep", "rest", "recovery"]):
        await update.message.reply_text(KNOWLEDGE["sleep"])
        return
    if any(w in msg for w in ["after workout", "post workout", "eat after gym"]):
        await update.message.reply_text(KNOWLEDGE["post_workout"])
        return

    # General goals
    if "weight loss" in msg:
        await update.message.reply_text(
            "📉 **Weight Loss Strategy:**\n- Calorie deficit\n- High protein, fiber\n- Limit processed foods\n- Strength + cardio training\n- Stay consistent!"
        )
        return
    if "muscle gain" in msg:
        await update.message.reply_text(
            "💪 **Muscle Gain Strategy:**\n- Calorie surplus\n- Protein 1.8-2.2g/kg\n- Compound lifts, progressive overload\n- Recovery & sleep\n- Supplements: protein, creatine"
        )
        return

    # Personalized diet (if user gives age, height, weight, activity)
    if any(w in msg for w in ["diet plan", "nutrition plan"]):
        await update.message.reply_text(
            "🍎 **Personalized Diet Tip:**\n"
            "Please provide your age, height, weight, and activity level for a custom plan.\n"
            "Otherwise, general guidelines:\n"
            "- Protein: 1.5-2.2g/kg\n"
            "- Complex carbs: brown rice, oats, sweet potatoes\n"
            "- Healthy fats: olive oil, nuts, avocado\n"
            "- Hydration: 3-4L water daily\n"
            "- Pre-workout: light carbs + protein\n"
            "- Post-workout: protein + fast carbs"
        )
        return

    # Greetings
    if any(w in msg for w in ["hi", "hello", "hey"]):
        await update.message.reply_text("👋 Hello! I'm FitCoach AI. Ask me about workouts, nutrition, recovery, or personalized diet tips!")
        return

    # Default response
    await update.message.reply_text(
        "💪 Ask me about specific workouts (chest, back, legs, biceps, triceps, shoulders), "
        "nutrition, recovery, or personalized diet tips!"
    )

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    while True:
        try:
            application.run_polling(drop_pending_updates=True)
        except Exception as e:
            logger.error(f"Polling error: {e}")
            time.sleep(10)
            continue

if __name__ == "__main__":
    main()
