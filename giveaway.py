from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode

from database import (
    is_giveaway_open,
    open_giveaway as db_open_giveaway,
    close_giveaway as db_close_giveaway,
    create_ticket,
    has_ticket,
    ticket_count,
)

BOT_USERNAME = "PingPoke_bot"   # Change if your bot username changes


# ----------------------------
# /opengiveaway
# ----------------------------
async def open_giveaway(update: Update, context: ContextTypes.DEFAULT_TYPE):

    db_open_giveaway()

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

    db_close_giveaway()

    await update.message.reply_text(
        "🔒 Giveaway Closed!\n\n"
        "No more ticket claims are accepted."
    )


# ----------------------------
# /tickets
# ----------------------------
async def close_giveaway(update: Update, context: ContextTypes.DEFAULT_TYPE):

    close_giveaway_db()

    await update.message.reply_text(
        "🔒 Giveaway Closed!\n\n"
        "No more ticket claims are accepted."
    )


# ----------------------------
# /tickets
# ----------------------------
async def tickets(update: Update, context: ContextTypes.DEFAULT_TYPE):

     total = ticket_count()

    status = "🟢 OPEN" if is_giveaway_open() else "🔴 CLOSED"

    await update.message.reply_text(
        f"🎟 Giveaway Statistics\n\n"
        f"Status: {status}\n"
        f"Tickets Claimed: {total}"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Only handle /start giveaway
    if not context.args or context.args[0] != "giveaway":
        await update.message.reply_text(
            "👋 Welcome to PingPoke Bot!"
        )
        return

    if not is_giveaway_open():
        await update.message.reply_text(
            "❌ The giveaway is currently closed."
        )
        return

    existing = has_ticket(update.effective_user.id)

    if existing:
        await update.message.reply_text(
            f"🎟 You already have Ticket #{existing[0]:03d}"
        )
        return

    ticket = create_ticket(update.effective_user)

    await update.message.reply_text(
        f"""🎉 Giveaway Registration Successful!

🎟 Your Ticket Number: #{ticket:03d}

Good luck! 🍀"""
    )
