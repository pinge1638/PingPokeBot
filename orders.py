from telegram import Update
from telegram.ext import ContextTypes

from database import (
    approve_order,
    reject_order,
)


async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_number = int(
        query.data.replace("approve_", "")
    )

    approve_order(order_number)

    await query.edit_message_caption(
        caption=query.message.caption + "\n\n✅ APPROVED"
    )


async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_number = int(
        query.data.replace("reject_", "")
    )

    reject_order(order_number)

    await query.edit_message_caption(
        caption=query.message.caption + "\n\n❌ REJECTED"
    )
