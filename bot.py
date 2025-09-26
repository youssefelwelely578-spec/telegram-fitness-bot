import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
from datetime import datetime, timedelta

# ----- Load Tokens from Environment -----
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# ----- User Data -----
user_profiles = {}
awaiting_profile = set()
user_access = {}  # Tracks trial start & premium status
TRIAL_DAYS = 3
VALID_CODE = "FITPREMIUM2025"

# ----- Helper: Check Access -----
def has_access(user_id):
    access = user_access.get(user_id)
    if not access:
        return False
    now = datetime.now()
    trial_end = access["trial_start"] + timedelta(days=TRIAL_DAYS)
    return access.get("premium", False) or now <= trial_end

# ----- /start -----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    now = datetime.now()
    if user_id not in user_access:
        user_access[user_id] = {"trial_start": now, "premium": False}
        await update.message.reply_text(
            "Welcome! 🎉 You have a 3-day free trial.\n"
            "Use /setprofile to start your personalized plan.\n"
            "Or type /pay to unlock premium immediately."
        )
    else:
        access = user_access[user_id]
        trial_end = access["trial_start"] + timedelta(days=TRIAL_DAYS)
        if access.get("premium"):
            await update.message.reply_text("Welcome back, Premium user! 🚀")
        elif now <= trial_end:
            await update.message.reply_text(
                f"Your free trial ends on {trial_end.strftime('%Y-%m-%d %H:%M:%S')}.\n"
                "Use /setprofile to continue or type /pay to unlock premium now."
            )
        else:
            await update.message.reply_text(
                "Your free trial has ended. 🔒\n"
                "Enter your premium code with /unlock <code> or type /pay to purchase premium."
            )

# ----- /pay -----
async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment_link = "https://www.patreon.com/posts/pro-fitness-139784356"
    await update.message.reply_text(
        f"💳 Get full premium access here:\n{payment_link}\n\n"
        "After payment, use /unlock FITPREMIUM2025 to activate premium access."
    )

# ----- /unlock -----
async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    args = context.args
    if not args:
        await update.message.reply_text("Please provide a code. Usage: /unlock <code>")
        return
    user_code = args[0].strip()
    if user_code == VALID_CODE:
        if user_id not in user_access:
            user_access[user_id] = {"trial_start": datetime.now(), "premium": True}
        else:
            user_access[user_id]["premium"] = True
        await update.message.reply_text("🎉 Premium access granted! You now have full access.")
    else:
        await update.message.reply_text("❌ Invalid code. Please check and try again.")

# ----- /setprofile -----
async def set_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not has_access(user_id):
        await update.message.reply_text("Your trial has ended. Please unlock premium to continue.")
        return
    awaiting_profile.add(user_id)
    await update.message.reply_text(
        "Enter your info in this format:\n"
        "Age, Weight(kg), Height(cm), Goal (lose fat / build muscle / maintain), Dietary preferences\n"
        "Example: 25, 75, 180, lose fat, no restrictions"
    )

# ----- /nutrition -----
async def nutrition_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not has_access(user_id):
        await update.message.reply_text("Your trial has ended. Please unlock premium to continue.")
        return
    profile = user_profiles.get(user_id)
    if not profile:
        await update.message.reply_text("Please set your profile first using /setprofile")
        return
    prompt = (
        f"Create a 7-day personalized nutrition plan:\n"
        f"Age: {profile['age']}\n"
        f"Weight: {profile['weight']} kg\n"
        f"Height: {profile['height']} cm\n"
        f"Goal: {profile['goal']}\n"
        f"Dietary preferences: {profile['diet']}\n"
        "Include meals, portion sizes, and calories."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional nutritionist and fitness coach."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600
        )
        await update.message.reply_text(response.choices[0].message.content)

        # Nutrition image
        img_response = client.images.generate(
            model="gpt-image-1",
            prompt=f"Illustration of a healthy meal plan for a person with goal {profile['goal']}",
            size="1024x1024"
        )
        await update.message.reply_photo(photo=img_response.data[0].url)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# ----- /workoutpic -----
async def generate_workout_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not has_access(user_id):
        await update.message.reply_text("Your trial has ended. Please unlock premium to continue.")
        return
    prompt = "Full-body workout routine, gym setting, realistic style"
    try:
        img_response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )
        await update.message.reply_photo(photo=img_response.data[0].url)
    except Exception as e:
        await update.message.reply_text(f"Error generating image: {e}")

# ----- General Q&A -----
async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    if not has_access(user_id):
        await update.message.reply_text("Your trial has ended. Please unlock premium to continue.")
        return

    # Profile input
    if user_id in awaiting_profile:
        try:
            age, weight, height, goal, diet = [x.strip() for x in text.split(",")]
            user_profiles[user_id] = {"age": age, "weight": weight, "height": height, "goal": goal, "diet": diet}
            awaiting_profile.remove(user_id)
            await update.message.reply_text("Profile saved! ✅ Now use /nutrition to get your personalized plan.")
        except Exception:
            await update.message.reply_text(
                "Invalid format. Follow: Age, Weight(kg), Height(cm), Goal, Dietary preferences"
            )
        return

    # AI Q&A
    prompt = (
        "You are a professional personal trainer and nutrition coach. "
        "Answer the user's question thoughtfully, provide workout tips, "
        "nutrition advice if relevant, and give motivation when appropriate.\n\n"
        f"User: {text}"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional personal trainer and motivational coach."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400
        )
        await update.message.reply_text(response.choices[0].message.content)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# ----- Main -----
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pay", pay))
    app.add_handler(CommandHandler("unlock", unlock))
    app.add_handler(CommandHandler("setprofile", set_profile))
    app.add_handler(CommandHandler("nutrition", nutrition_plan))
    app.add_handler(CommandHandler("workoutpic", generate_workout_image))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_messages))
    app.run_polling()

if __name__ == "__main__":
    main()
