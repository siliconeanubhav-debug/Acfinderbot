import logging
from bot import app
from webserver import keep_alive

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    keep_alive()
    print("🚀 AC Post & Story Finder Bot Starting...")
    app.run()
  
