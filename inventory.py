from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

import config

# Conversation States
NAME = 0
DESCRIPTION = 1
CATEGORY = 2
TYPE = 3
COST = 4
PRICE = 5
STOCK = 6


async def addproduct(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Owner only
    if update.effective_user.id != config.OWNER_ID:
        await update.message.reply_text(
            "⛔ You are not allowed to use this command."
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "📦 Let's add a new product!\n\n"
        "What's the product name?"
    )

    return NAME


async def product_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["name"] = update.message.text

    await update.message.reply_text(
        "📝 Enter a description.\n\n"
        "Type /skip if there isn't one."
    )

    return DESCRIPTION

async def product_description(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["description"] = update.message.text

    keyboard = [
        [InlineKeyboardButton("🟡 Pokémon", callback_data="cat_pokemon")],
        [InlineKeyboardButton("🏴‍☠️ One Piece", callback_data="cat_onepiece")],
        [InlineKeyboardButton("🎁 Accessories", callback_data="cat_accessories")],
    ]

    await update.message.reply_text(
        "📂 Choose a Category",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return ConversationHandler.WAITING


async def skip_description(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["description"] = ""

    keyboard = [
        [InlineKeyboardButton("🟡 Pokémon", callback_data="cat_pokemon")],
        [InlineKeyboardButton("🏴‍☠️ One Piece", callback_data="cat_onepiece")],
        [InlineKeyboardButton("🎁 Accessories", callback_data="cat_accessories")],
    ]

    await update.message.reply_text(
        "📂 Choose a Category",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return ConversationHandler.WAITING

async def category_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "cat_pokemon":
        context.user_data["category"] = "Pokemon"

    elif query.data == "cat_onepiece":
        context.user_data["category"] = "One Piece"

    elif query.data == "cat_accessories":
        context.user_data["category"] = "Accessories"

    keyboard = [
        [InlineKeyboardButton("📦 Ready Stock", callback_data="type_ready")],
        [InlineKeyboardButton("🚢 Preorder", callback_data="type_preorder")],
    ]

    await query.edit_message_text(
        f"✅ Category: {context.user_data['category']}\n\n"
        "Choose Product Type",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return TYPE


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "❌ Product creation cancelled."
    )

    return ConversationHandler.END
