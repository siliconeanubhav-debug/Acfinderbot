import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from config import Config
from database import db

# India Standard Timezone Constant
IST = ZoneInfo("Asia/Kolkata")


# --- 1. TIME & GREETING HELPERS ---

def parse_time(time_str: str) -> timedelta | None:
    """
    Parses human-readable time strings into a timedelta object.
    Supports: m (minutes), h (hours), d (days), w (weeks)
    Examples: '30m', '12h', '1d', '2w', '1d12h'
    """
    if not time_str:
        return None

    pattern = r'(\d+)\s*([mhdw])'
    matches = re.findall(pattern, time_str.lower())

    if not matches:
        return None

    total_seconds = 0
    for value, unit in matches:
        val = int(value)
        if unit == 'm':
            total_seconds += val * 60
        elif unit == 'h':
            total_seconds += val * 3600
        elif unit == 'd':
            total_seconds += val * 86400
        elif unit == 'w':
            total_seconds += val * 604800

    return timedelta(seconds=total_seconds) if total_seconds > 0 else None


def format_time(seconds: int) -> str:
    """
    Formats total seconds into readable Days, Hours, Minutes.
    Example: 9000 seconds -> '2h 30m'
    """
    if seconds <= 0:
        return "0m"

    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or not parts:
        parts.append(f"{minutes}m")

    return " ".join(parts)


def get_time_greeting() -> str:
    """Returns dynamic time-based greetings strictly in Asia/Kolkata timezone."""
    current_hour = datetime.now(IST).hour
    if 5 <= current_hour < 12:
        return "Good Morning ☀️"
    elif 12 <= current_hour < 17:
        return "Good Afternoon 🌤️"
    elif 17 <= current_hour < 22:
        return "Good Evening 🌆"
    else:
        return "Good Night 🌙"


# --- 2. PREMIUM UTILITY HELPERS ---

async def add_premium_user(user_id: int, time_str: str = None):
    """
    Utility wrapper to add premium using time string (e.g., '1d', '12h', '30m').
    Returns (success: bool, formatted_time_str: str)
    """
    duration = parse_time(time_str) if time_str else None
    await db.make_premium(user_id, duration)
    
    if duration:
        formatted = format_time(int(duration.total_seconds()))
    else:
        formatted = "Lifetime ♾️"
        
    return True, formatted


async def remove_premium_user(user_id: int):
    """Utility wrapper to remove premium from database."""
    await db.remove_premium(user_id)
    return True


async def check_user_premium(user_id: int) -> bool:
    """Utility wrapper to check if user has active premium."""
    return await db.is_premium_user(user_id)


# --- 3. TEXT & AUTH HELPERS ---

def extract_first_line(text: str) -> str:
    """Extracts only the first line of a given text."""
    if not text:
        return ""
    lines = text.strip().split("\n")
    return lines[0].strip()


async def check_force_sub(bot: Client, user_id: int) -> bool:
    """Checks whether the user has joined the force subscription channel."""
    fsub_channel = getattr(Config, "FSUB_CHANNEL", None)
    if not fsub_channel:
        return True
    try:
        member = await bot.get_chat_member(fsub_channel, user_id)
        return member.status not in ["kicked", "left"]
    except UserNotParticipant:
        return False
    except Exception:
        return True


def is_admin(user_id: int) -> bool:
    """Checks if the user ID exists in the admin list."""
    return int(user_id) in getattr(Config, "ADMINS", [])


# --- 4. UI BUTTON HELPERS ---

def get_start_buttons():
    """Generates standard start menu inline buttons."""
    buttons = [
        [
            InlineKeyboardButton("📖 ɢᴜɪᴅᴇ", callback_data="cb_guide"),
            InlineKeyboardButton("✨ ғᴇᴀᴛᴜʀᴇs", callback_data="cb_features")
        ],
        [
            InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴs", callback_data="cb_plans"),
            InlineKeyboardButton("👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url=Config.DEV_LINK)
        ],
        [
            InlineKeyboardButton("📢 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url=Config.UPDATE_CHANNEL),
            InlineKeyboardButton("💬 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ", url=Config.SUPPORT_GROUP)
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def get_back_button():
    """Generates a simple 'Back to Home' button."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ", callback_data="cb_home")]
    ])
