import re
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from fuzzywuzzy import fuzz, process
from database import db

EXACT_MATCH_THRESHOLD = 60  # Direct result if score >= 60
SUGGESTION_THRESHOLD = 30   # "Did You Mean" if score between 30 and 59
                            # Below 30 = SILENT MODE


def clean_text(text: str) -> str:
    """Cleans text for clear matching."""
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip().lower()


@Client.on_message(filters.private & filters.text & ~filters.command(["start", "help", "about"]))
async def search_handler(bot: Client, message: Message):
    query = message.text.strip()
    
    if len(query) < 2:
        return

    # Fetch all stored posts/stories from Mongo DB
    all_posts = await db.get_all_posts()
    
    if not all_posts:
        # Database Empty -> Silent Mode
        return

    # Map titles and store indexed data
    titles_list = []
    posts_data = []

    for post in all_posts:
        raw_title = post.get("title", "")
        link = post.get("link", "")
        if not raw_title or not link:
            continue

        # Rule: First Line Title Only
        first_line_title = raw_title.split("\n")[0].strip()
        if first_line_title:
            titles_list.append(first_line_title)
            posts_data.append({
                "id": str(post.get("_id", len(posts_data))),
                "title": first_line_title,
                "link": link
            })

    if not titles_list:
        return

    cleaned_query = clean_text(query)
    
    # Fuzzy match using fuzzywuzzy
    best_matches = process.extract(
        cleaned_query,
        titles_list,
        scorer=fuzz.WRatio,
        limit=5
    )

    exact_matches = []
    suggestion_matches = []

    for match_title, score in best_matches:
        # Find item corresponding to match_title
        for item in posts_data:
            if item["title"] == match_title:
                if score >= EXACT_MATCH_THRESHOLD:
                    exact_matches.append(item)
                elif score >= SUGGESTION_THRESHOLD:
                    suggestion_matches.append(item)
                break

    # 1. DIRECT MATCH (Score >= 60)
    if exact_matches:
        reply_text = f"<b>🔍 sᴇᴀʀᴄʜ ʀᴇsᴜʟᴛs ғᴏʀ:</b> <code>{query}</code>\n\n"
        buttons = []
        for item in exact_matches:
            title = item["title"]
            label = f"✨ {title[:35]}..." if len(title) > 35 else f"✨ {title}"
            buttons.append([InlineKeyboardButton(label, url=item["link"])])

        await message.reply_text(
            text=reply_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
        return

    # 2. DID YOU MEAN SUGGESTIONS (30 <= Score < 60)
    elif suggestion_matches:
        reply_text = (
            f"<b>🤔 ᴅɪᴅ ʏᴏᴜ ᴍᴇᴀɴ ᴏɴᴇ ᴏғ ᴛʜᴇsᴇ?</b>\n\n"
            f"<i>ᴄʟɪᴄᴋ ᴏɴ ᴀ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ sᴛᴏʀʏ:</i>"
        )
        buttons = []
        for idx, item in enumerate(suggestion_matches[:5]):
            title = item["title"]
            label = f"❓ {title[:35]}..." if len(title) > 35 else f"❓ {title}"
            # Pass clean identifier in callback data
            buttons.append([InlineKeyboardButton(label, callback_data=f"sgst_{idx}")])

        # Store suggestion cache/titles temporarily in bot state or handle via text mapping
        await message.reply_text(
            text=reply_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
        return

    # 3. SILENT MODE (Score < 30)
    else:
        return


# --- CALLBACK HANDLER FOR "DID YOU MEAN" BUTTON CLICKS ---

@Client.on_callback_query(filters.regex(r"^sgst_"))
async def suggestion_callback_handler(bot: Client, query: CallbackQuery):
    await query.answer()

    # Extract clicked button label
    clicked_title = ""
    for row in query.message.reply_markup.inline_keyboard:
        for btn in row:
            if btn.callback_data == query.data:
                clicked_title = btn.text.replace("❓ ", "").replace("...", "").strip()
                break

    all_posts = await db.get_all_posts()
    matched_link = None
    matched_full_title = ""

    # Search for link in Mongo DB
    for post in all_posts:
        raw_title = post.get("title", "")
        first_line = raw_title.split("\n")[0].strip()
        if clicked_title.lower() in first_line.lower():
            matched_link = post.get("link", "")
            matched_full_title = first_line
            break

    # Target chat ID and Message
    chat_id = query.message.chat.id

    # 1. DELETE THE PREVIOUS "DID YOU MEAN" MESSAGE
    try:
        await query.message.delete()
    except Exception:
        pass

    # 2. SEND THE FINAL STORY LINK MESSAGE
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
