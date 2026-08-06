from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    ContextTypes,
)

from database import (
    get_products,
    get_product_details,
)

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

async def shop_type(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "shop_ready":
        product_type = "Ready Stock"

    else:
        product_type = "Preorder"

    category = context.user_data["shop_category"]

    rows = get_products()

    keyboard = []

    for product_id, name, cat, ptype, cost, price, stock in rows:

        if cat != category:
            continue

        if ptype != product_type:
            continue

        keyboard.append([
            InlineKeyboardButton(
                f"{name} • ${price:.2f} • Stock {stock}",
                callback_data=f"product_{product_id}"
            )
        ])

    if not keyboard:
        await query.edit_message_text(
            "❌ No products available."
        )
        return

    await query.edit_message_text(
        f"📦 {category}\n{product_type}\n\nChoose a product:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def product_page(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    product_id = query.data.replace("product_", "")

    product = get_product_details(product_id)

    if not product:
        await query.edit_message_text("❌ Product not found.")
        return

    (
        product_id,
        name,
        category,
        product_type,
        cost,
        price,
        stock,
    ) = product

    context.user_data["selected_product"] = product_id

    keyboard = [
        [
            InlineKeyboardButton(
                "🛒 Add to Cart",
                callback_data="cart_add",
            )
        ]
    ]

    await query.edit_message_text(
        f"""📦 {name}

💰 Price: ${price:.2f}

📦 Stock: {stock}

Choose an option below.""",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
