from telegram import Update
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


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "❌ Product creation cancelled."
    )

    return ConversationHandler.END
