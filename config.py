import os

class Config:
    API_ID = int(os.environ.get("API_ID", "123456"))
    API_HASH = os.environ.get("API_HASH", "YOUR_API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")
    
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://...")
    DB_NAME = os.environ.get("DB_NAME", "ACSearchBotDB")
    
    # Admins Parsing with Safety Fallback
    raw_admins = os.environ.get("ADMINS", "123456789")
    ADMINS = [int(x.strip()) for x in raw_admins.split(",") if x.strip().isdigit()]
    
    # Force Subscribe Channel Username (@ रिमूव सेफ्टी के साथ)
    raw_fsub = os.environ.get("FSUB_CHANNEL", "YourChannelUsername").replace("@", "").strip()
    FSUB_CHANNEL = raw_fsub if raw_fsub else None
    FSUB_LINK = f"https://t.me/{FSUB_CHANNEL}" if FSUB_CHANNEL else "https://t.me/YourChannelUsername"
    
    # Dynamic Links & Developer Contact
    UPDATE_CHANNEL = os.environ.get("UPDATE_CHANNEL", "https://t.me/YourChannelUsername")
    SUPPORT_GROUP = os.environ.get("SUPPORT_GROUP", "https://t.me/YourSupportGroup")
    DEV_LINK = os.environ.get("DEV_LINK", "https://t.me/Kaluu")
