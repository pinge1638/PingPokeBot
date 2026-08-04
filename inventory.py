from telegram import Update
from telegram.ext import ContextTypes

import config

from database import add_product


async def addproduct(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != config.OWNER_ID:
        await update.message.reply_text(
            "⛔ This command is only available to the owner."
        )
        return

    await update.message.reply_text(
        "📦 Inventory system is connected successfully!"
    )
