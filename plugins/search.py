import re
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from fuzzywuzzy import fuzz, process
from database import db

# Threshold Scores
EXACT_MATCH_THRESHOLD = 60  # Direct result if score >= 60
SUGGESTION_THRESHOLD = 30   # Show "Did You Mean" if score is between 30 and 59
                            # Below 30 = SILENT MODE


def clean_text(text: str) -> str:
    """Cleans text for better fuzzy matching."""
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip().lower()


@Client.on_message(filters.private & filters.text & ~filters.command(["start", "help", "about"]))
async def fuzzy_search_handler(bot: Client, message: Message):
    query = message.text.strip()
    
    if len(query) < 2:
        return

    # Fetch all stored stories from Mongo DB
    all_posts = await db.get_all_posts()
    
    if not all_posts:
        # DB Empty -> Silent Mode
        return

    # Map only the FIRST LINE of each post title
    titles_map = {}
    for post in all_posts:
        raw_title = post.get("title", "")
        if not raw_title:
            continue
            
        first_line_title = raw_title.split("\n")[0].strip()
        link = post.get("link", "")
        
        if first_line_title:
            titles_map[first_line_title] = link

    titles_list = list(titles_map.keys())
    if not titles_list:
        return

    cleaned_query = clean_text(query)
    
    # Get top 5 fuzzy matches using fuzzywuzzy
    best_matches = process.extract(
        cleaned_query,
        titles_list,
        scorer=fuzz.WRatio,
        limit=5
    )

    exact_matches = []
    suggestion_matches = []

    for match_title, score in best_matches:
        if score >= EXACT_MATCH_THRESHOLD:
            exact_matches.append((match_title, titles_map[match_title]))
        elif score >= SUGGESTION_THRESHOLD:
            suggestion_matches.append((match_title, titles_map[match_title]))

    # 1. DIRECT MATCH FOUND (Score >= 60)
    if exact_matches:
        reply_text = f"<b>🔍 sᴇᴀʀᴄʜ ʀᴇsᴜʟᴛs ғᴏʀ:</b> <code>{query}</code>\n\n"
        buttons = []
        for title, link in exact_matches:
            button_label = f"✨ {title[:35]}..." if len(title) > 35 else f"✨ {title}"
            buttons.append([InlineKeyboardButton(button_label, url=link)])

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
            f"<i>ᴄʟɪᴄᴋ ᴏɴ ᴀ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ Yᴏᴜʀ sᴛᴏʀʏ:</i>"
        )
        buttons = []
        # Store index or title reference in callback data
        for idx, (title, link) in enumerate(suggestion_matches):
            button_label = f"❓ {title[:35]}..." if len(title) > 35 else f"❓ {title}"
            # Pass custom callback prefix for suggestions
            buttons.append([InlineKeyboardButton(button_label, callback_data=f"sgst_{idx}_{query[:10]}")])

        # Temporarily store matches context or handle dynamic link fetching
        await message.reply_text(
            text=reply_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
        return

    # 3. SILENT MODE (Score < 30)
    else:
        return


# --- HANDLER FOR "DID YOU MEAN" BUTTON CLICKS ---

@Client.on_callback_query(filters.regex(r"^sgst_"))
async def suggestion_callback_handler(bot: Client, query: CallbackQuery):
    await query.answer()

    # Get clicked button text/title from the message
    # To find the exact clicked item, we match the button label or search DB again
    clicked_button_text = ""
    for row in query.message.reply_markup.inline_keyboard:
        for btn in row:
            if btn.callback_data == query.data:
                # Remove emoji prefix (❓ ) to get the title
                clicked_button_text = btn.text.replace("❓ ", "").replace("...", "").strip()
                break

    all_posts = await db.get_all_posts()
    matched_link = None
    matched_full_title = ""

    # Find matching link in DB
    for post in all_posts:
        raw_title = post.get("title", "")
        first_line = raw_title.split("\n")[0].strip()
        if clicked_button_text.lower() in first_line.lower():
            matched_link = post.get("link", "")
            matched_full_title = first_line
            break

    # DELETE THE PREVIOUS "DID YOU MEAN" MESSAGE
    try:
        await query.message.delete()
    except Exception:
        pass

    # SEND THE FINAL STORY RESULT
    if matched_link:
        reply_text = f"<b>✨ ʜᴇʀᴇ ɪs ʏᴏᴜʀ sᴛᴏʀʏ:</b>\n\n<b>📖 {matched_full_title}</b>"
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ᴏᴘᴇɴ", url=matched_link)]
        ])
        await query.message.reply_to_message.reply_text(
            text=reply_text,
            reply_markup=buttons,
            disable_web_page_preview=True
        )
    else:
        await query.message.reply_to_message.reply_text("<b>❌ Story link not found or expired.</b>")
