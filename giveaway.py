from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode

from database import (
    is_giveaway_open,
    open_giveaway,
    close_giveaway,
    create_ticket,
    ticket_count,
)

BOT_USERNAME = "PingPoke_bot"   # Change if your bot username changes


# ----------------------------
# /opengiveaway
# ----------------------------
async def open_giveaway(update: Update, context: ContextTypes.DEFAULT_TYPE):

    set_giveaway_status(True)

    keyboard = [
        [
            InlineKeyboardButton(
                "🎟 Claim Ticket",
                url=f"https://t.me/{BOT_USERNAME}?start=giveaway",
            )
        ]
    ]

    await update.message.reply_text(
        "🎉 *PINGPOKE GIVEAWAY IS NOW OPEN!*\n\n"
        "Press the button below to claim your giveaway ticket.\n\n"
        "Only one ticket per Telegram account.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ----------------------------
# /closegiveaway
# ----------------------------
async def close_giveaway(update: Update, context: ContextTypes.DEFAULT_TYPE):

    set_giveaway_status(False)

    await update.message.reply_text(
        "🔒 Giveaway Closed!\n\n"
        "No more ticket claims are accepted."
    )


# ----------------------------
# /tickets
# ----------------------------
async def tickets(update: Update, context: ContextTypes.DEFAULT_TYPE):

    total = get_ticket_count()

    status = "🟢 OPEN" if is_giveaway_open() else "🔴 CLOSED"

    await update.message.reply_text(
        f"🎟 Giveaway Statistics\n\n"
        f"Status: {status}\n"
        f"Tickets Claimed: {total}"
    )
