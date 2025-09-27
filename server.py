import os
from flask import Flask, request
from bot import build_app

app = Flask(__name__)
telegram_app = build_app()

@app.route("/")
def home():
    return "AI Personal Trainer Bot is live!", 200

@app.route(f"/{os.getenv('8426717766:AAGeYeMKt4wetni8l85LyUx_PsdnTF5Ue5E')}", methods=["POST"])
async def webhook():
    update = request.get_json(force=True)
    await telegram_app.update_queue.put(update)
    return "ok", 200
