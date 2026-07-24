import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)
import config

ANTI_SPAM = [
    "t.me/","telegram.me/","joinchat",
    "onlyfans","crypto","btc","usdt","binance","porn","sex"
]

from giveaway import (
    open_giveaway,
    close_giveaway,
    tickets,
    start,
)

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("PING command received")
    await update.message.reply_text("Pong!")

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    count = await context.bot.get_chat_member_count(update.effective_chat.id)

    for member in update.message.new_chat_members:
        keyboard = [
            [InlineKeyboardButton("⚡ Pokémon Product Menu", url=config.POKEMON_TOPIC)],
            [InlineKeyboardButton("🏴‍☠️ One Piece Product Menu", url=config.ONEPIECE_TOPIC)],
            [InlineKeyboardButton("🎉 Giveaways", url=config.GIVEAWAY_TOPIC)],
            [InlineKeyboardButton("📰 TCG News & Leaks", url=config.NEWS_TOPIC)],
            [InlineKeyboardButton("📢 Announcements", url=config.ANNOUNCEMENT_TOPIC)],
        ]

        msg = await update.message.reply_html(
f"""👋 Welcome {member.mention_html()}!

🇯🇵 <b>Welcome to PingPoke!</b>

You are <b>Member #{count}</b> 🎉

Please explore our community using the buttons below.

Happy Collecting! 💙""",
reply_markup=InlineKeyboardMarkup(keyboard)
        )

        await asyncio.sleep(300)
        try:
            await msg.delete()
        except:
            pass

async def anti_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()

    if any(word in text for word in ANTI_SPAM):
        try:
            await update.message.delete()
        except:
            pass
            
# ===============================
# GIVEAWAY SYSTEM
# ===============================

# database setup

# /opengiveaway

# /closegiveaway

# /tickets

# /list

# /export

# callback button

# claim ticket

# ===============================

import logging

logging.basicConfig(level=logging.INFO)

app = ApplicationBuilder().token(config.BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anti_spam))

app.add_handler(CommandHandler("ping", ping))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("opengiveaway", open_giveaway))
app.add_handler(CommandHandler("closegiveaway", close_giveaway))
app.add_handler(CommandHandler("tickets", tickets))

async def error_handler(update, context):
    print("ERROR:", context.error)

app.add_error_handler(error_handler)

print("PingPokeBot running...")
app.run_polling(
    drop_pending_updates=True,
    allowed_updates=Update.ALL_TYPES,
    poll_interval=1,
)
