import asyncio

from admin import admin, admin_buttons
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

import config

ANTI_SPAM = [
    "t.me/","telegram.me/","joinchat",
    "onlyfans","crypto","btc","usdt","binance","porn","sex"
]

from shop import (
    shop,
    shop_category,
    shop_type,
    product_page,
    add_cart,
    continue_shop,
    checkout,
    choose_quantity,
    delivery_method,
    back_cart,
    paynow,
    paid,
    payment_screenshot,
    WAIT_PAYMENT,
    plus_item,
    minus_item,
    delete_item,
)
from orders import (
    approve,
    reject,
)


from giveaway import (
    open_giveaway,
    close_giveaway,
    tickets,
    list_entries,
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

from inventory import (
    addproduct,
    addstock,
    addstock_select,
    addstock_amount,
    products,
    product_name,
    product_description,
    skip_description,
    category_buttons,
    type_buttons,
    product_cost,
    product_price,
    product_stock,
    cancel,
    NAME,
    DESCRIPTION,
    CATEGORY,
    TYPE,
    COST,
    PRICE,
    STOCK,
    ADD_STOCK_SELECT,
    ADD_STOCK_AMOUNT,
    removestock,
    removestock_select,
    removestock_amount,
    REMOVE_STOCK_SELECT,
    REMOVE_STOCK_AMOUNT,
    sell,
    sell_select,
    sell_quantity,
    sell_customer,
    sell_payment,
    SELL_SELECT,
    SELL_QUANTITY,
    SELL_CUSTOMER,
    SELL_PAYMENT,
    )

product_conv = ConversationHandler(
    entry_points=[
        CommandHandler("addproduct", addproduct),
    ],
    states={
        NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, product_name)
        ],

        DESCRIPTION: [
            CommandHandler("skip", skip_description),
            MessageHandler(filters.TEXT & ~filters.COMMAND, product_description),
        ],

        CATEGORY: [
            CallbackQueryHandler(category_buttons, pattern="^cat_"),
        ],

        TYPE: [
            CallbackQueryHandler(type_buttons, pattern="^type_"),
        ],
    
        COST: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, product_cost)
        ],
    
        PRICE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, product_price)
        ],
    
        STOCK: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, product_stock)
        ],
    },

    
    fallbacks=[
        CommandHandler("cancel", cancel)
    ],
)



app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
stock_conv = ConversationHandler(
    entry_points=[
        CommandHandler("addstock", addstock),
    ],
    states={
        ADD_STOCK_SELECT: [
            CallbackQueryHandler(addstock_select, pattern="^stock_"),
        ],

        ADD_STOCK_AMOUNT: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                addstock_amount,
            ),
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel),
    ],
)
remove_stock_conv = ConversationHandler(
    entry_points=[
        CommandHandler("removestock", removestock),
    ],
    states={
        REMOVE_STOCK_SELECT: [
            CallbackQueryHandler(removestock_select, pattern="^remove_"),
        ],

        REMOVE_STOCK_AMOUNT: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                removestock_amount,
            ),
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel),
    ],
)
sell_conv = ConversationHandler(
    entry_points=[
        CommandHandler("sell", sell),
    ],
    states={
        SELL_SELECT: [
            CallbackQueryHandler(
                sell_select,
                pattern="^sell_",
            ),
        ],

        SELL_QUANTITY: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                sell_quantity,
            ),
        ],

        SELL_CUSTOMER: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                sell_customer,
            ),
        ],

        SELL_PAYMENT: [
            CallbackQueryHandler(
                sell_payment,
                pattern="^pay_",
            ),
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel),
    ],
)
app.add_handler(product_conv)
app.add_handler(stock_conv)
app.add_handler(remove_stock_conv)
app.add_handler(sell_conv)
app.add_handler(CommandHandler("shop", shop))

app.add_handler(
    CallbackQueryHandler(
        shop_category,
        pattern="^shop_(pokemon|onepiece|accessories)$",
    )
)

app.add_handler(
    CallbackQueryHandler(
        shop_type,
        pattern="^shop_(ready|preorder)$",
    )
)

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anti_spam))
app.add_handler(CommandHandler("admin", admin))
app.add_handler(CommandHandler("products", products))

app.add_handler(
    CallbackQueryHandler(
        admin_buttons,
        pattern="^(inventory|orders|preorders|payments|giveaway|reports|settings|back_admin|orders_pending|orders_approved|orders_rejected|vieworder_\d+)$"
    )
)

app.add_handler(
    CallbackQueryHandler(
        product_page,
        pattern="^product_",
    )
)
app.add_handler(
    CallbackQueryHandler(
        add_cart,
        pattern="^cart_",
    )
)
app.add_handler(
    CallbackQueryHandler(
        continue_shop,
        pattern="^continue_shop$",
    )
)
app.add_handler(
    CallbackQueryHandler(
        choose_quantity,
        pattern="^qty_",
    )
)
app.add_handler(
    CallbackQueryHandler(
        checkout,
        pattern="^checkout$",
    )
)
app.add_handler(
    CallbackQueryHandler(
        delivery_method,
        pattern="^delivery_",
    )
)
app.add_handler(
    CallbackQueryHandler(
        back_cart,
        pattern="^back_cart$",
    )
)
app.add_handler(
    CallbackQueryHandler(
        paynow,
        pattern="^paynow$",
    )
)
payment_conv = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            paid,
            pattern="^paid$",
        )
    ],
    states={
        WAIT_PAYMENT: [
            MessageHandler(
                filters.PHOTO,
                payment_screenshot,
            )
        ]
    },
    fallbacks=[],
)
app.add_handler(payment_conv)
app.add_handler(
    CallbackQueryHandler(
        approve,
        pattern="^approve_",
    )
)

app.add_handler(
    CallbackQueryHandler(
        reject,
        pattern="^reject_",
    )
)
app.add_handler(
    CallbackQueryHandler(
        plus_item,
        pattern="^plus_",
    )
)

app.add_handler(
    CallbackQueryHandler(
        minus_item,
        pattern="^minus_",
    )
)

app.add_handler(
    CallbackQueryHandler(
        delete_item,
        pattern="^delete_",
    )
)
app.add_handler(CommandHandler("ping", ping))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("opengiveaway", open_giveaway))
app.add_handler(CommandHandler("closegiveaway", close_giveaway))
app.add_handler(CommandHandler("tickets", tickets))
app.add_handler(CommandHandler("list", list_entries))

async def error_handler(update, context):
    print("ERROR:", context.error)

app.add_error_handler(error_handler)

print("PingPokeBot running...")
app.run_polling(
    drop_pending_updates=True,
    allowed_updates=Update.ALL_TYPES,
    poll_interval=1,
)
