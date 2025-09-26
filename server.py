# server.py
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

if __name__ == "__main__":
    # Bind to Render Free assigned port
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
