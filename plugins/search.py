import re
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from fuzzywuzzy import fuzz
from database import db

EXACT_MATCH_THRESHOLD = 50  # 50% ya usse zyada match hone par direct link
SUGGESTION_THRESHOLD = 25   # 25% se 49% match hone par "Did You Mean"
                            # 25% se kam hone par Silent Mode


def clean_text(text: str) -> str:
    """Removes special characters for clean search."""
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip().lower()


@Client.on_message(filters.private & filters.text & ~filters.command(["start", "help", "about"]))
async def search_handler(bot: Client, message: Message):
    query = message.text.strip()
    
    if len(query) < 2:
        return

    # Fetch posts from MongoDB
    all_posts = await db.get_all_posts()
    
    # Debug print (Server Terminal par check karne ke liye)
    print(f"DEBUG: Search Query -> '{query}' | Total Posts in DB -> {len(all_posts)}")

    if not all_posts:
        # DB Khali hai -> Silent Mode
        return

    clean_query = clean_text(query)
    exact_matches = []
    suggestion_matches = []

    for post in all_posts:
        raw_title = post.get("title", "")
        link = post.get("link", "")
        
        if not raw_title or not link:
            continue

        # RULE: Sirf Pehli Line (First Line Title Only)
        first_line_title = raw_title.split("\n")[0].strip()
        clean_title = clean_text(first_line_title)

        # 1. Direct Word Presence Check (Agar query title me moojood hai)
        if clean_query in clean_title or clean_title in clean_query:
            score = 95
        else:
            # 2. Fuzzy Matching Score using FuzzyWuzzy
            score = fuzz.partial_ratio(clean_query, clean_title)

        item = {
            "title": first_line_title,
            "link": link,
            "score": score
        }

        if score >= EXACT_MATCH_THRESHOLD:
            exact_matches.append(item)
        elif score >= SUGGESTION_THRESHOLD:
            suggestion_matches.append(item)

    # Sort results by match score (highest first)
    exact_matches.sort(key=lambda x: x["score"], reverse=True)
    suggestion_matches.sort(key=lambda x: x["score"], reverse=True)

    # --- 1. DIRECT MATCH FOUND (Score >= 50) ---
    if exact_matches:
        reply_text = f"<b>🔍 sᴇᴀʀᴄʜ ʀᴇsᴜʟᴛs ғᴏʀ:</b> <code>{query}</code>\n\n"
        buttons = []
        for item in exact_matches[:5]:
            title = item["title"]
            label = f"✨ {title[:35]}..." if len(title) > 35 else f"✨ {title}"
            buttons.append([InlineKeyboardButton(label, url=item["link"])])

        await message.reply_text(
            text=reply_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
        return

    # --- 2. DID YOU MEAN SUGGESTIONS (25 <= Score < 50) ---
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

        await message.reply_text(
            text=reply_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
        return

    # --- 3. SILENT MODE (Score < 25) ---
    else:
        return


# --- CALLBACK HANDLER FOR "DID YOU MEAN" BUTTON CLICKS ---

@Client.on_callback_query(filters.regex(r"^sgst_"))
async def suggestion_callback_handler(bot: Client, query: CallbackQuery):
    await query.answer()

    # Get clicked button label text
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

    # 1. Delete previous "Did You Mean" message
    try:
        await query.message.delete()
    except Exception:
        pass

    # 2. Send the final Story Link
    if matched_link:
        reply_text = (
            f"<b>✨ ʜᴇʀᴇ ɪs ʏᴏᴜʀ sᴛᴏʀʏ:</b>\n\n"
            f"<b>📖 {matched_full_title}</b>"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ᴏᴘᴇɴ", url=matched_link)]
        ])
        await bot.send_message(
            chat_id=chat_id,
            text=reply_text,
            reply_markup=buttons,
            disable_web_page_preview=True
        )
    else:
        await bot.send_message(
            chat_id=chat_id,
            text="<b>❌ Story link not found or expired.</b>"
        )
