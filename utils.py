from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from config import Config

def extract_first_line(text: str) -> str:
    if not text:
        return ""
    lines = text.strip().split("\n")
    return lines[0].strip()

async def check_force_sub(bot: Client, user_id: int) -> bool:
    if not Config.FSUB_CHANNEL:
        return True
    try:
        member = await bot.get_chat_member(Config.FSUB_CHANNEL, user_id)
        return member.status not in ["kicked", "left"]
    except UserNotParticipant:
        return False
    except Exception:
        return True

def is_admin(user_id: int) -> bool:
    return user_id in Config.ADMINS

def get_start_buttons():
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
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ", callback_data="cb_home")]
    ])
