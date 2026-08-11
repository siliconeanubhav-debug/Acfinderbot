import math
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import db

ITEMS_PER_PAGE = 10
AUTO_DELETE_TIME = 300  # 5 Minutes


def build_filter_keyboard(posts, page: int, total_pages: int):
    """Generates inline pagination buttons for navigation."""
    buttons = []
    
    # Navigation Row (Back / Page Info / Next)
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("◀️ Back", callback_data=f"fltr_page_{page - 1}"))
    
    nav_buttons.append(InlineKeyboardButton(f"📜 {page}/{total_pages}", callback_data="fltr_noop"))
    
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"fltr_page_{page + 1}"))
    
    buttons.append(nav_buttons)
    buttons.append([InlineKeyboardButton("❌ Close", callback_data="fltr_close")])
    
    return InlineKeyboardMarkup(buttons)


async def get_filter_page_text(posts, page: int, total_pages: int, total_count: int) -> str:
    """Formats the page text with mono-spaced story titles for one-tap copy."""
    start_idx = (page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    current_posts = posts[start_idx:end_idx]

    text = f"📚 <b><u>Total Stories Available:</u> {total_count}</b>\n"
    text += f"<i>(Tap on any story title to copy it instantly)</i>\n\n"

    for idx, post in enumerate(current_posts, start=start_idx + 1):
        raw_title = post.get("title", "Untitled")
        first_line = raw_title.split("\n")[0].strip()
        
        # Mono-spaced code text for easy tap-to-copy
        text += f"<b>{idx}.</b> <code>{first_line}</code>\n"

    text += f"\n<i>📄 Page {page} of {total_pages}</i>"
    text += "\n\n<i>⏳ This message will be auto-deleted in 5 minutes.</i>"
    return text


@Client.on_message(filters.private & filters.command("filter"))
async def filter_list_command(bot: Client, message: Message):
    all_posts = await db.get_all_posts()

    if not all_posts:
        return await message.reply_text("❌ <b>No stories found in database!</b>")

    total_count = len(all_posts)
    total_pages = math.ceil(total_count / ITEMS_PER_PAGE)
    page = 1

    text = await get_filter_page_text(all_posts, page, total_pages, total_count)
    markup = build_filter_keyboard(all_posts, page, total_pages)

    sent_msg = await message.reply_text(
        text=text,
        reply_markup=markup,
        disable_web_page_preview=True
    )

    # Auto-delete after 5 minutes
    asyncio.create_task(auto_delete_message(sent_msg, AUTO_DELETE_TIME))


@Client.on_callback_query(filters.regex(r"^fltr_"))
async def filter_pagination_handler(bot: Client, query: CallbackQuery):
    data = query.data

    if data == "fltr_noop":
        return await query.answer("📄 Current Page", show_alert=False)

    if data == "fltr_close":
        try:
            await query.message.delete()
        except Exception:
            pass
        return await query.answer("Closed!")

    if data.startswith("fltr_page_"):
        page = int(data.split("_")[2])
        all_posts = await db.get_all_posts()

        if not all_posts:
            await query.answer("No posts found!", show_alert=True)
            return

        total_count = len(all_posts)
        total_pages = math.ceil(total_count / ITEMS_PER_PAGE)

        if page < 1 or page > total_pages:
            return await query.answer("Invalid Page!", show_alert=True)

        text = await get_filter_page_text(all_posts, page, total_pages, total_count)
        markup = build_filter_keyboard(all_posts, page, total_pages)

        try:
            await query.message.edit_text(
                text=text,
                reply_markup=markup,
                disable_web_page_preview=True
            )
            await query.answer()
        except Exception:
            await query.answer()


async def auto_delete_message(message: Message, delay: int):
    """Deletes message after given seconds delay."""
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception:
        pass
