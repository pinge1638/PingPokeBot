from telegram import Update
from telegram.ext import ContextTypes

from database import (
    approve_order,
    reject_order,
    get_order,
)


async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    order_number = int(
        query.data.replace("approve_", "")
    )

    success = approve_order(order_number)

    order = get_order(order_number)

    if not order:
        await query.answer(
            "❌ Order not found.",
            show_alert=True,
        )
        return

    telegram_id = order[0]

    if not success:
        await query.answer(
            "❌ Cannot approve this order. It may already be approved or there may not be enough stock.",
            show_alert=True,
        )
        return

    await context.bot.send_message(
        chat_id=telegram_id,
        text=f"""
✅ Payment Approved!

Order #{order_number}

Thank you for your purchase!

Your order is now being prepared.
"""
    )

    if query.message.photo:
        await query.edit_message_caption(
            caption=query.message.caption + "\n\n✅ APPROVED"
        )
    else:
        await query.edit_message_text(
            text=query.message.text + "\n\n✅ APPROVED",
            reply_markup=None,
        )


async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    order_number = int(
        query.data.replace("reject_", "")
    )

    reject_order(order_number)

    order = get_order(order_number)

    if not order:
        await query.answer(
            "❌ Order not found.",
            show_alert=True,
        )
        return

    telegram_id = order[0]

    await context.bot.send_message(
        chat_id=telegram_id,
        text=f"""
❌ Payment Rejected

Order #{order_number}

Please contact the admin if you believe this was a mistake.
"""
    )

    if query.message.photo:
        await query.edit_message_caption(
            caption=query.message.caption + "\n\n❌ REJECTED"
        )
    else:
        await query.edit_message_text(
            text=query.message.text + "\n\n❌ REJECTED",
            reply_markup=None,
        )
