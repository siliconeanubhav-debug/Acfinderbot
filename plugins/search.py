import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import db

try:
    from rapidfuzz import fuzz
except ImportError:
    from fuzzywuzzy import fuzz

# Configuration
EXACT_MATCH_THRESHOLD = 60   # 60% ya usse zyada accurate match hone par direct story
SUGGESTION_THRESHOLD = 40    # 40% se 59% accurate match hone par "Did You Mean"
                             # 40% se kam match -> STRICT SILENT MODE (No False Buttons)
AUTO_DELETE_TIME = 300       # Auto-delete time in seconds (5 Minutes)


def clean_text(text: str) -> str:
    """Removes symbols and converts text to lowercase."""
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip().lower()


@Client.on_message(filters.private & filters.text & ~filters.command(["start", "help", "about", "add", "delete", "premium", "make_premium", "remove_premium", "addstory", "delstory", "rmstory", "addpremium", "removepremium"]))
async def strict_fuzzy_search_handler(bot: Client, message: Message):
    text = message.text.strip()

    # 1. Ignore Commands, URLs, and Extremely Short Queries
    if text.startswith("/") or text.startswith("http://") or text.startswith("https://") or len(text) < 2:
        return

    all_posts = await db.get_all_posts()
    if not all_posts:
        return

    clean_query = clean_text(text)
    query_words = clean_query.split()

    exact_matches = []
    suggestion_matches = []

    for post in all_posts:
        raw_title = post.get("title", "")
        link = post.get("link", "")

        if not raw_title or not link:
            continue

        # RULE: Save/Fetch FIRST LINE only as title
        first_line_title = raw_title.split("\n")[0].strip()
        clean_title = clean_text(first_line_title)

        if not clean_title:
            continue

        # Skip irrelevant test entries if user didn't explicitly search for them
        if "test" in clean_title and "test" not in clean_query:
            continue

        # 2. STRICT WORD ACCURACY CHECK
        fuzzy_score = fuzz.token_set_ratio(clean_query, clean_title)

        # Bonus score check if search words are present inside the title
        word_overlap = sum(1 for word in query_words if word in clean_title)
        if word_overlap == 0 and fuzzy_score < 65:
            # Drop matches that don't share actual words
            continue

        item = {
            "title": first_line_title,
            "link": link,
            "score": fuzzy_score
        }

        if fuzzy_score >= EXACT_MATCH_THRESHOLD:
            exact_matches.append(item)
        elif fuzzy_score >= SUGGESTION_THRESHOLD:
            suggestion_matches.append(item)

    # Sort results by score (Highest first)
    exact_matches.sort(key=lambda x: x["score"], reverse=True)
    suggestion_matches.sort(key=lambda x: x["score"], reverse=True)

    delete_notice = "\n\n<i>⏳ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇᴅ ɪɴ 𝟻 ᴍɪɴᴜᴛᴇs.</i>"

    # --- A. DIRECT EXACT MATCH (Score >= 60) ---
    if exact_matches:
        reply_text = f"<b>🔍 sᴇᴀʀᴄʜ ʀᴇsᴜʟᴛs ғᴏʀ:</b> <code>{text}</code>\n\n"
        buttons = []
        for item in exact_matches[:5]:
            title = item["title"]
            label = f"✨ {title[:35]}..." if len(title) > 35 else f"✨ {title}"
            buttons.append([InlineKeyboardButton(label, url=item["link"])])

        sent_msg = await message.reply_text(
            text=reply_text + delete_notice,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
        
        # Auto-delete after 5 minutes
        asyncio.create_task(auto_delete_message(sent_msg, AUTO_DELETE_TIME))
        return

    # --- B. ACCURATE DID YOU MEAN SUGGESTIONS (Score 40-59) ---
    elif suggestion_matches:
        reply_text = (
            f"<b>🤔 ᴅɪᴅ ʏᴏᴜ ᴍᴇᴀɴ ᴏɴᴇ ᴏғ ᴛʜᴇsᴇ?</b>\n\n"
            f"<i>ᴄʟɪᴄᴋ ᴏɴ ᴀ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ sᴛᴏʀʏ:</i>"
        )
        buttons = []
        for idx, item in enumerate(suggestion_matches[:5]):
            title = item["title"]
            label = f"❓ {title[:35]}..." if len(title) > 35 else f"❓ {title}"
            buttons.append([InlineKeyboardButton(label, callback_data=f"sgst_{idx}")])

        sent_msg = await message.reply_text(
            text=reply_text + delete_notice,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )

        # Auto-delete after 5 minutes
        asyncio.create_task(auto_delete_message(sent_msg, AUTO_DELETE_TIME))
        return

    # --- C. STRICT SILENT MODE (Out of DB -> No output) ---
    else:
        return


# --- CALLBACK HANDLER FOR "DID YOU MEAN" BUTTONS ---

@Client.on_callback_query(filters.regex(r"^sgst_"))
async def suggestion_callback_handler(bot: Client, query: CallbackQuery):
    await query.answer()

    clicked_title = ""
    if query.message and query.message.reply_markup:
        for row in query.message.reply_markup.inline_keyboard:
            for btn in row:
                if btn.callback_data == query.data:
                    clicked_title = btn.text.replace("❓ ", "").replace("...", "").strip()
                    break

    all_posts = await db.get_all_posts()
    matched_link = None
    matched_full_title = ""

    if clicked_title and all_posts:
        for post in all_posts:
            raw_title = post.get("title", "")
            first_line = raw_title.split("\n")[0].strip()
            if clicked_title.lower() in first_line.lower():
                matched_link = post.get("link", "")
                matched_full_title = first_line
                break

    chat_id = query.message.chat.id

    # Delete previous "Did You Mean" message safely
    try:
        await query.message.delete()
    except Exception:
        pass

    delete_notice = "\n\n<i>⏳ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇᴅ ɪɴ 𝟻 ᴍɪɴᴜᴛᴇs.</i>"

    # Send final story link message
    if matched_link:
        reply_text = (
            f"<b>✨ ʜᴇʀᴇ ɪs ʏᴏᴜʀ sᴛᴏʀʏ:</b>\n\n"
            f"<b>📖 {matched_full_title}</b>"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ᴏᴘᴇɴ", url=matched_link)]
        ])
        sent_msg = await bot.send_message(
            chat_id=chat_id,
            text=reply_text + delete_notice,
            reply_markup=buttons,
            disable_web_page_preview=True
        )
        asyncio.create_task(auto_delete_message(sent_msg, AUTO_DELETE_TIME))
    else:
        await bot.send_message(
            chat_id=chat_id,
            text="<b>❌ Story link not found or expired.</b>"
        )


async def auto_delete_message(message: Message, delay: int):
    """Deletes a message after a specified delay in seconds."""
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception:
        pass
