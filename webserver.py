import os
import logging
from flask import Flask
from threading import Thread

# Suppress noisy Werkzeug/Flask ping logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask('')

@app.route('/')
def home():
    return "🚀 AC Search Bot is Alive & Running!"

def run():
    # Fetch port from environment variables (Render/Koyeb/Heroku compatibility)
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run, daemon=True)
    t.start()
