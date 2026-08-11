from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from utils import get_start_buttons, get_back_button
from database import db

START_TEXT = (
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
    first_name = message.from_user.first_name
    
    await db.add_user(user_id, first_name)
    await message.reply_text(
        text=START_TEXT,
        reply_markup=get_start_buttons(),
        disable_web_page_preview=True
    )

@Client.on_callback_query(filters.regex("^cb_"))
async def callback_handler(bot: Client, query: CallbackQuery):
    data = query.data

    if data == "cb_home":
        await query.message.edit_text(
            text=START_TEXT,
            reply_markup=get_start_buttons(),
            disable_web_page_preview=True
        )

    elif data == "cb_guide":
        text = (
            "<b>📖 ʜᴏᴡ ᴛᴏ ᴜsᴇ:</b>\n\n"
            "<b>1. sᴇᴀʀᴄʜ:</b> sɪᴍᴘʟʏ ᴛʏᴘᴇ ᴀɴʏ ᴋᴇʏᴡᴏʀᴅ or ᴛɪᴛʟᴇ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ.\n"
            "<b>2. ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ:</b> ɪғ ᴀ ᴍᴀᴛᴄʜ ɪs ғᴏᴜɴᴅ, ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴀᴄᴄᴇss ᴛʜᴇ ʟɪɴᴋ.\n"
            "<b>3. sɪʟᴇɴᴛ ᴍᴏᴅᴇ:</b> ɪғ ɴᴏ ᴍᴀᴛᴄʜ ᴇxɪsᴛs, ᴛʜᴇ ʙᴏᴛ sᴛᴀʏs Cᴏᴍᴘʟᴇᴛᴇʟʏ sɪʟᴇɴᴛ."
        )
        await query.message.edit_text(text=text, reply_markup=get_back_button())

    elif data == "cb_features":
        text = (
            "<b>🔥 ʙᴏᴛ ғᴇᴀᴛᴜʀᴇs:</b>\n\n"
            "• <b>ᴀᴜᴛᴏ-ɪɴᴅᴜᴄᴛɪᴏɴ:</b> ᴄʜᴀɴɴᴇʟ ᴘᴏsᴛs ᴀʀᴇ sᴀᴠᴇᴅ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ.\n"
            "• <b>sᴍᴀʀᴛ ғᴜᴢᴢʏ sᴇᴀʀᴄʜ:</b> Fᴀsᴛ ᴀɴᴅ ᴀᴄᴄᴜʀᴀᴛᴇ ʀᴇsᴜʟᴛs.\n"
            "• <b>ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss:</b> Uɴʟɪᴍɪᴛᴇᴅ sᴇᴀʀᴄʜ ᴡɪᴛʜᴏᴜᴛ Rᴇsᴛʀɪᴄᴛɪᴏɴs."
        )
        await query.message.edit_text(text=text, reply_markup=get_back_button())

    elif data == "cb_plans":
        text = (
            "<b>💎 ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴs:</b>\n\n"
            "• <b>$1.00 / 1 ᴍᴏɴᴛʜ</b> — ᴜɴʟɪᴍɪᴛᴇᴅ sᴇᴀʀᴄʜ & ᴅɪʀᴇᴄᴛ ᴀᴄᴄᴇss\n"
            "• <b>$2.50 / 3 ᴍᴏɴᴛʜs</b> — ᴅɪsᴄᴏᴜɴᴛᴇᴅ Plan\n\n"
            "ᴄᴏɴᴛᴀᴄᴛ Developer ᴛᴏ ᴀᴄᴛɪᴠᴀᴛᴇ Your Plan."
        )
        await query.message.edit_text(text=text, reply_markup=get_back_button())
