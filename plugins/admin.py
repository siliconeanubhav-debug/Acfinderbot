from pyrogram import Client, filters
from pyrogram.types import Message
from utils import is_admin, parse_time, format_time, get_time_greeting
from database import db


@Client.on_message(filters.command("addpremium") & filters.private)
async def add_premium_cmd(bot: Client, message: Message):
    if not is_admin(message.from_user.id):
        return

    # command logic: /addpremium <user_id> <time> (e.g. /addpremium 123456789 1d12h or 30m)
    if len(message.command) < 3:
        greeting = get_time_greeting()
        return await message.reply_text(
            f"✨ <b>{greeting}!</b>\n\n"
            "❌ <b>ᴜsᴀɢᴇ:</b> <code>/addpremium <user_id> <time></code>\n\n"
            "<b>⏱️ ᴛɪᴍᴇ ғᴏʀᴍᴀᴛs:</b>\n"
            "• <code>30m</code> = 30 Minutes\n"
            "• <code>12h</code> = 12 Hours\n"
            "• <code>1d</code> = 1 Day\n"
            "• <code>1d12h30m</code> = 1 Day, 12 Hours & 30 Mins"
        )

    try:
        target_user_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Enter a valid User ID.")

    time_str = message.command[2]
    duration = parse_time(time_str)

    if not duration:
        return await message.reply_text("❌ <b>ɪɴᴠᴀʟɪᴅ ᴛɪᴍᴇ ғᴏʀᴍᴀᴛ!</b> Use m, h, d, or w (e.g., 30m, 12h, 1d).")

    # Save to MongoDB with IST timezone awareness
    await db.make_premium(target_user_id, duration)
    
    formatted_duration = format_time(int(duration.total_seconds()))
    await message.reply_text(
        f"✨ <b>ᴜsᴇʀ <code>{target_user_id}</code> ᴜᴘɢʀᴀᴅᴇᴅ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ!</b>\n\n"
        f"⏳ <b>ᴅᴜʀᴀᴛɪᴏɴ:</b> <code>{formatted_duration}</code>"
    )

    # Notify User
    try:
        await bot.send_message(
            chat_id=target_user_id,
            text=(
                "🎉 <b>CONGRATULATIONS! YOUR PREMIUM HAS BEEN ACTIVATED!</b>\n\n"
                f"⏳ <b>Valid For:</b> <code>{formatted_duration}</code>\n"
                "🚀 Enjoy unlimited fast search and instant access!"
            )
        )
    except Exception:
        pass


@Client.on_message(filters.command("removepremium") & filters.private)
async def remove_premium_cmd(bot: Client, message: Message):
    if not is_admin(message.from_user.id):
        return

    if len(message.command) < 2:
        return await message.reply_text("❌ <b>ᴜsᴀɢᴇ:</b> <code>/removepremium <user_id></code>")

    try:
        target_user_id = int(message.command[1])
        await db.remove_premium(target_user_id)
        await message.reply_text(f"🗑️ <b>ᴘʀᴇᴍɪᴜᴍ sᴛᴀᴛᴜs ʀᴇᴍᴏᴠᴇᴅ ғᴏʀ <code>{target_user_id}</code>!</b>")
        
        # Notify User
        try:
            await bot.send_message(
                chat_id=target_user_id,
                text="⚠️ <b>Your Premium subscription status has expired or was removed by admin.</b>"
            )
        except Exception:
            pass
    except ValueError:
        await message.reply_text("❌ Enter a valid User ID.")


@Client.on_message(filters.command("addstory") & filters.private)
async def add_story_cmd(bot: Client, message: Message):
    if not is_admin(message.from_user.id):
        return

    if " " not in message.text or "|" not in message.text:
        return await message.reply_text(
            "❌ <b>ғᴏʀᴍᴀᴛ:</b> <code>/addstory Title | https://t.me/...</code>"
        )

    content = message.text.split(" ", 1)[1]
    title, link = content.split("|", 1)
    
    # Save post to database (Ensures only first line of title is indexable)
    await db.add_post(title.strip(), link.strip())
    await message.reply_text("✅ <b>sᴛᴏʀʏ sᴀᴠᴇᴅ ᴛᴏ ᴅᴀᴛᴀʙᴀsᴇ!</b>")


@Client.on_message(filters.command(["delstory", "rmstory"]) & filters.private)
async def delete_story_cmd(bot: Client, message: Message):
    if not is_admin(message.from_user.id):
        return

    if len(message.command) < 2:
        return await message.reply_text("❌ <b>ᴜsᴀɢᴇ:</b> <code>/delstory <exact story title></code>")

    story_title = message.text.split(" ", 1)[1].strip()
    deleted = await db.delete_post(story_title)

    if deleted:
        await message.reply_text(f"🗑️ <b>Story '<code>{story_title}</code>' deleted from database!</b>")
    else:
        await message.reply_text("❌ <b>No story found with that title!</b>")
