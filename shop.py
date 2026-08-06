from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    ContextTypes,
)
from database import get_products

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("🟡 Pokémon", callback_data="shop_pokemon")],
        [InlineKeyboardButton("🏴‍☠️ One Piece", callback_data="shop_onepiece")],
        [InlineKeyboardButton("🎁 Accessories", callback_data="shop_accessories")],
    ]

    await update.message.reply_text(
        "🛍 Welcome to PingPoke!\n\n"
        "Please choose a category.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def shop_category(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "shop_pokemon":
        context.user_data["shop_category"] = "Pokemon"

    elif query.data == "shop_onepiece":
        context.user_data["shop_category"] = "One Piece"

    elif query.data == "shop_accessories":
        context.user_data["shop_category"] = "Accessories"

    keyboard = [
        [InlineKeyboardButton("📦 Ready Stock", callback_data="shop_ready")],
        [InlineKeyboardButton("🚢 Preorder", callback_data="shop_preorder")],
    ]

    await query.edit_message_text(
        f"📂 {context.user_data['shop_category']}\n\n"
        "Choose Product Type",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
