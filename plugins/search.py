from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from utils import check_force_sub
from database import db
from config import Config

@Client.on_message(filters.text & ~filters.command(["start", "addpremium", "removepremium", "addstory"]))
async def search_handler(bot: Client, message: Message):
    user_id = message.from_user.id
    query = message.text.strip()

    if len(query) < 2:
        return

    # 1. Database Search
    results = await db.search_posts(query=query, limit=5)

    # SILENT MODE: Completely silent if no database matches are found
    if not results:
        return

    # 2. Force Subscribe Verification
    is_joined = await check_force_sub(bot, user_id)
    if not is_joined:
        buttons = [[InlineKeyboardButton("📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=Config.FSUB_LINK)]]
        await message.reply_text(
            f"🎉 <b>ʏᴏᴜʀ sᴛᴏʀʏ/ᴘᴏsᴛ ʜᴀs ʙᴇᴇɴ ғᴏᴜɴᴅ!</b>\n\n, ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴀᴄᴄᴇss the ʟɪɴᴋ.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    # 3. Deliver Search Results
    reply_text = f"<b>🔍 sᴇᴀʀᴄʜ ʀᴇsᴜʟᴛs ғᴏʀ: '<code>{query}</code>'</b>\n\n"
    buttons = []

    for idx, item in enumerate(results, 1):
        reply_text += f"<b>{idx}.</b> {item['title']}\n"
        buttons.append([InlineKeyboardButton(f"🔗 ɢᴇᴛ ʟɪɴᴋ #{idx}", url=item['link'])])

    await message.reply_text(
        reply_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )
