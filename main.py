import logging
from zoneinfo import ZoneInfo
from bot import app
from webserver import keep_alive

# Timezone check for India Standard Time
IST = ZoneInfo("Asia/Kolkata")

# Basic Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ACSearchBot")

if __name__ == "__main__":
    # Render / Koyeb / Heroku keep alive server
    keep_alive()
    
    logger.info("🚀 AC Post & Story Finder Bot Starting in Asia/Kolkata timezone...")
    
    try:
        app.run()
    except Exception as e:
        logger.critical(f"❌ Bot stopped due to critical error: {e}", exc_info=True)
