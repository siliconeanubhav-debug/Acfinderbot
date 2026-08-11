import html
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.errors import MessageNotModified
from utils import get_start_buttons, get_back_button, get_time_greeting
from database import db


def get_start_text(first_name: str) -> str:
    """Generates dynamic start text with IST greeting and user name."""
    greeting = get_time_greeting()
    safe_name = html.escape(first_name)
    
    return (
        f"<b>{greeting}, {safe_name}! 👋</b>\n\n"
        "<b>✨ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴀᴄ ᴘᴏsᴛ & sᴛᴏʀʏ ғɪɴᴅᴇʀ ʙᴏᴛ ✨</b>\n\n"
        "<i>ɪ ᴀᴍ ᴛʜᴇ ᴍᴏsᴛ ᴘᴏᴡᴇʀғᴜʟ ᴀɴᴅ ᴀᴜᴛᴏᴍᴀᴛᴇᴅ ᴄʜᴀɴɴᴇʟ ʟɪɴᴋ sᴇᴀʀᴄʜ ᴇɴɢɪɴᴇ.</i>\n\n"
        "<b>⚡ key ғᴇᴀᴛᴜʀᴇs:</b>\n"
        "• ᴀᴜᴛᴏ-ɪɴᴅᴜᴄᴛɪᴏɴ sʏsᴛᴇᴍ\n"
        "• sᴍᴀʀᴛ & ғᴀsᴛ sᴇᴀʀᴄʜ\n"
        "• ᴘʀᴇᴍɪᴜᴍ ᴄᴏɴᴛᴇɴᴛ ᴀᴄᴄᴇss\n\n"
        "👇 ᴜsᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ɴᴀᴠɪɢᴀᴛᴇ:"
    )


@Client.on_message(filters.command("start") & filters.private)
async def start_command(bot: Client, message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "User"
    
    # Register/Update User in DB
    await db.add_user(user_id, first_name)
    
    start_text = get_start_text(first_name)
    await message.reply_text(
        text=start_text,
        reply_markup=get_start_buttons(),
        disable_web_page_preview=True
    )


@Client.on_callback_query(filters.regex("^cb_"))
async def callback_handler(bot: Client, query: CallbackQuery):
    data = query.data
    first_name = query.from_user.first_name or "User"
    
    # Stop loading spinner on Telegram button
    await query.answer()

    try:
        if data == "cb_home":
            start_text = get_start_text(first_name)
            await query.message.edit_text(
                text=start_text,
                reply_markup=get_start_buttons(),
                disable_web_page_preview=True
            )

        elif data == "cb_guide":
            text = (
                "<b>📖 ʜᴏᴡ ᴛᴏ ᴜsᴇ:</b>\n\n"
                "<b>1. sᴇᴀʀᴄʜ:</b> sɪᴍᴘʟʏ ᴛʏᴘᴇ ᴀɴʏ ᴋᴇʏᴡᴏʀᴅ or ᴛɪᴛʟᴇ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ.\n"
                "<b>2. ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ:</b> ɪғ ᴀ ᴍᴀᴛᴄʜ ɪs ғᴏᴜɴᴅ, ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴀᴄᴄᴇss ᴛʜᴇ ʟɪɴᴋ.\n"
                "<b>3. sɪʟᴇɴᴛ ᴍᴏᴅᴇ:</b> ɪғ ɴᴏ ᴍᴀᴛᴄʜ ᴇxɪsᴛs, ᴛʜᴇ ʙᴏᴛ sᴛᴀʏs ᴄᴏᴍᴘʟᴇᴛᴇʟʏ sɪʟᴇɴᴛ."
            )
            await query.message.edit_text(text=text, reply_markup=get_back_button())

        elif data == "cb_features":
            text = (
                "<b>🔥 ʙᴏᴛ ғᴇᴀᴛᴜʀᴇs:</b>\n\n"
                "• <b>ᴀᴜᴛᴏ-ɪɴᴅᴜᴄᴛɪᴏɴ:</b> ᴄʜᴀɴɴᴇʟ ᴘᴏsᴛs ᴀʀᴇ sᴀᴠᴇᴅ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ.\n"
                "• <b>sᴍᴀʀᴛ ғᴜᴢᴢʏ sᴇᴀʀᴄʜ:</b> ғᴀsᴛ ᴀɴᴅ ᴀᴄᴄᴜʀᴀᴛᴇ ʀᴇsᴜʟᴛs.\n"
                "• <b>ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss:</b> ᴜɴʟɪᴍɪᴛᴇᴅ sᴇᴀʀᴄʜ ᴡɪᴛʜᴏᴜᴛ ʀᴇsᴛʀɪᴄᴛɪᴏɴs."
            )
            await query.message.edit_text(text=text, reply_markup=get_back_button())

        elif data == "cb_plans":
            text = (
                "<b>💎 ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴs:</b>\n\n"
                "• <b>$1.00 / 1 ᴍᴏɴᴛʜ</b> — ᴜɴʟɪᴍɪᴛᴇᴅ sᴇᴀʀᴄʜ & ᴅɪʀᴇᴄᴛ ᴀᴄᴄᴇss\n"
                "• <b>$2.50 / 3 ᴍᴏɴᴛʜs</b> — ᴅɪsᴄᴏᴜɴᴛᴇᴅ ᴘʟᴀɴ\n\n"
                "ᴄᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ ᴀᴄᴛɪᴠᴀᴛᴇ ʏᴏᴜʀ ᴘʟᴀɴ."
            )
            await query.message.edit_text(text=text, reply_markup=get_back_button())

    except MessageNotModified:
        pass
    except Exception as e:
        print(f"Callback Error: {e}")
