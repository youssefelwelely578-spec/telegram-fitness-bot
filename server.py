from flask import Flask, request
import os
from bot import handle_update, bot  # import your bot logic

app = Flask(__name__)

@app.route("/")
def home():
    return "Telegram AI Personal Trainer is running!"

# Webhook endpoint for Telegram
@app.route(f"/{os.getenv('8426717766:AAGeYeMKt4wetni8l85LyUx_PsdnTF5Ue5E')}", methods=["POST"])
def webhook():
    update = request.get_json(force=True)
    handle_update(update)  # call function from bot.py
    return "ok", 200

if __name__ == "__main__":
    # Render sets PORT automatically
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
