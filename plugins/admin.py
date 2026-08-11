from pyrogram import Client, filters
from pyrogram.types import Message
from utils import is_admin
from database import db

@Client.on_message(filters.command("addpremium") & filters.private)
async def add_premium_cmd(bot: Client, message: Message):
    if not is_admin(message.from_user.id):
        return
    if len(message.command) < 2:
        return await message.reply_text("❌ <b>ᴜsᴀɢᴇ:</b> <code>/addpremium <user_id></code>")
    
    try:
        user_id = int(message.command[1])
        await db.make_premium(user_id)
        await message.reply_text(f"✨ <b>ᴜsᴇʀ <code>{user_id}</code> ᴜᴘɢʀᴀᴅᴇᴅ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ!</b>")
    except ValueError:
        await message.reply_text("❌ Enter a valid User ID.")

@Client.on_message(filters.command("removepremium") & filters.private)
async def remove_premium_cmd(bot: Client, message: Message):
    if not is_admin(message.from_user.id):
        return
    if len(message.command) < 2:
        return await message.reply_text("❌ <b>ᴜsᴀɢᴇ:</b> <code>/removepremium <user_id></code>")
    
    try:
        user_id = int(message.command[1])
        await db.remove_premium(user_id)
        await message.reply_text(f"🗑️ <b>ᴘʀᴇᴍɪᴜᴍ sᴛᴀᴛᴜs ʀᴇᴍᴏᴠᴇᴅ ғᴏʀ <code>{user_id}</code>!</b>")
    except ValueError:
        await message.reply_text("❌ Enter a valid User ID.")

@Client.on_message(filters.command("addstory") & filters.private)
async def add_story_cmd(bot: Client, message: Message):
    if not is_admin(message.from_user.id):
        return
    if " " not in message.text or "|" not in message.text:
        return await message.reply_text("❌ <b>ғᴏʀᴍᴀᴛ:</b> <code>/addstory Title | https://t.me/...</code>")
    
    content = message.text.split(" ", 1)[1]
    title, link = content.split("|", 1)
    await db.add_post(title.strip(), link.strip())
    await message.reply_text("✅ <b>sᴛᴏʀʏ sᴀᴠᴇᴅ ᴛᴏ ᴅᴀᴛᴀʙᴀsᴇ!</b>")
