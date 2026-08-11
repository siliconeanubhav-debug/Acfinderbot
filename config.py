import os

class Config:
    API_ID = int(os.environ.get("API_ID", "123456"))
    API_HASH = os.environ.get("API_HASH", "YOUR_API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")
    
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://...")
    DB_NAME = os.environ.get("DB_NAME", "ACSearchBotDB")
    
    # Admins (Comma-separated IDs)
    ADMINS = [int(id) for id in os.environ.get("ADMINS", "123456789").split()]
    
    # Force Subscribe Channel Username (without @)
    FSUB_CHANNEL = os.environ.get("FSUB_CHANNEL", "YourChannelUsername")
    FSUB_LINK = f"https://t.me/{FSUB_CHANNEL}"
    
    # Links
    UPDATE_CHANNEL = os.environ.get("UPDATE_CHANNEL", "https://t.me/YourChannelUsername")
    SUPPORT_GROUP = os.environ.get("SUPPORT_GROUP", "https://t.me/YourSupportGroup")
    DEV_LINK = os.environ.get("DEV_LINK", "https://t.me/Kaluu")
  
