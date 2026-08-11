import re
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from rapidfuzz import process, fuzz
from database import db

# Threshold score for fuzzy matching (0 - 100)
# 60 means if match score is less than 60%, bot remains SILENT
FUZZY_THRESHOLD = 60


def clean_text(text: str) -> str:
    """Removes special characters and extra spaces for cleaner search matching."""
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip().lower()


@Client.on_message(filters.private & filters.text & ~filters.command(["start", "help", "about"]))
async def fuzzy_search_handler(bot: Client, message: Message):
    query = message.text.strip()
    
    # Ignore very short messages to prevent unnecessary processing
    if len(query) < 2:
        return

    # Fetch all posts/stories from Mongo DB
    all_posts = await db.get_all_posts() # Ensure get_all_posts() returns a list of dicts with 'title' and 'link'
    
    if not all_posts:
        # Out of DB / Empty Database -> Silent Mode
        return

    # Extract clean titles (first lines) for fuzzy matching
    titles_map = {}
    for post in all_posts:
        raw_title = post.get("title", "")
        # Take only the first line of the title if multiple lines exist
        first_line_title = raw_title.split("\n")[0].strip()
        if first_line_title:
            titles_map[first_line_title] = post.get("link", "")

    titles_list = list(titles_map.keys())
    if not titles_list:
        return

    # Perform Fuzzy Match using rapidfuzz
    cleaned_query = clean_text(query)
    best_matches = process.extract(
        cleaned_query,
        titles_list,
        scorer=fuzz.WRatio,
        limit=5
    )

    # Filter matches that meet the similarity threshold
    matched_results = []
    for match_title, score, index in best_matches:
        if score >= FUZZY_THRESHOLD:
            link = titles_map[match_title]
            matched_results.append((match_title, link, score))

    # SILENT MODE: If no result matches the minimum threshold, remain completely silent
    if not matched_results:
        return

    # Construct UI Response
    reply_text = f"<b>🔍 sᴇᴀʀᴄʜ ʀᴇsᴜʟᴛs ғᴏʀ:</b> <code>{query}</code>\n\n"
    buttons = []

    for title, link, score in matched_results:
        # Truncate long titles for neat inline button view
        button_label = f"✨ {title[:35]}..." if len(title) > 35 else f"✨ {title}"
        buttons.append([InlineKeyboardButton(button_label, url=link)])

    keyboard = InlineKeyboardMarkup(buttons)

    await message.reply_text(
        text=reply_text,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )
