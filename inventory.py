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
from database import (
    add_product,
    get_products,
    get_product,
    get_product_sale,
    add_stock,
    remove_stock,
    record_sale,
)
# Conversation States
NAME = 0
DESCRIPTION = 1
CATEGORY = 2
TYPE = 3
COST = 4
PRICE = 5
STOCK = 6
ADD_STOCK_SELECT = 7
ADD_STOCK_AMOUNT = 8
REMOVE_STOCK_SELECT = 9
REMOVE_STOCK_AMOUNT = 10
SELL_SELECT = 11
SELL_QUANTITY = 12
SELL_CUSTOMER = 13
SELL_PAYMENT = 14


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

    return CATEGORY


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

    return CATEGORY

async def category_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(">>> category_buttons")
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


async def type_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(">>> type_buttons")
    query = update.callback_query
    await query.answer()

    if query.data == "type_ready":
        context.user_data["type"] = "Ready Stock"

    elif query.data == "type_preorder":
        context.user_data["type"] = "Preorder"

    await query.edit_message_text(
        f"""✅ Category: {context.user_data['category']}
✅ Type: {context.user_data['type']}

💰 Enter Cost Price"""
    )

    return COST

async def product_cost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(">>> product_cost")
    print(">>> product_cost reached")

    context.user_data["cost"] = float(update.message.text)

    await update.message.reply_text(
        "💵 Enter Selling Price"
    )

    return PRICE


async def product_price(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["price"] = float(update.message.text)

    await update.message.reply_text(
        "📦 Enter Stock Quantity"
    )

    return STOCK

async def product_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["stock"] = int(update.message.text)
    add_product(
        product_id=context.user_data["name"].lower().replace(" ", "_"),
        name=context.user_data["name"],
        category=context.user_data["category"],
        product_type=context.user_data["type"],
        cost=context.user_data["cost"],
        price=context.user_data["price"],
        stock=context.user_data["stock"],
    )
    await update.message.reply_text(
        f"""
✅ Product Created!

📦 Name:
{context.user_data['name']}

📝 Description:
{context.user_data['description'] or "-"}

📂 Category:
{context.user_data['category']}

📦 Type:
{context.user_data['type']}

💰 Cost:
${context.user_data['cost']:.2f}

💵 Selling:
${context.user_data['price']:.2f}

📦 Stock:
{context.user_data['stock']}
"""
    )

    return ConversationHandler.END
async def products(update: Update, context: ContextTypes.DEFAULT_TYPE):

    rows = get_products()

    if not rows:
        await update.message.reply_text("📦 No products found.")
        return

    text = "📦 *Current Inventory*\n\n"

    for product_id, name, category, product_type, cost, price, stock in rows:
        text += (
            f"📦 *{name}*\n"
            f"🆔 {product_id}\n"
            f"📂 {category}\n"
            f"📦 {product_type}\n"
            f"💰 Cost: ${cost:.2f}\n"
            f"💵 Selling: ${price:.2f}\n"
            f"📦 Stock: {stock}\n\n"
        )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
    )

async def addstock(update: Update, context: ContextTypes.DEFAULT_TYPE):

    rows = get_products()

    if not rows:
        await update.message.reply_text("📦 No products found.")
        return ConversationHandler.END

    keyboard = []

    for product_id, name, *_ in rows:
        keyboard.append([
            InlineKeyboardButton(
                name,
                callback_data=f"stock_{product_id}"
            )
        ])

    await update.message.reply_text(
        "📦 Select a product:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return ADD_STOCK_SELECT

async def addstock_select(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    product_id = query.data.replace("stock_", "")

    product = get_product(product_id)

    if not product:
        await query.edit_message_text("❌ Product not found.")
        return ConversationHandler.END

    context.user_data["stock_product"] = product_id

    _, name, stock = product

    await query.edit_message_text(
        f"""📦 {name}

Current Stock: {stock}

➕ How many would you like to add?"""
    )

    return ADD_STOCK_AMOUNT

async def addstock_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):

    quantity = int(update.message.text)

    product_id = context.user_data["stock_product"]

    product = get_product(product_id)

    _, name, old_stock = product

    add_stock(product_id, quantity)

    new_stock = old_stock + quantity

    await update.message.reply_text(
        f"""✅ Stock Updated!

📦 {name}

Old Stock: {old_stock}
Added: {quantity}

New Stock: {new_stock}"""
    )

    return ConversationHandler.END

async def removestock(update: Update, context: ContextTypes.DEFAULT_TYPE):

    rows = get_products()

    if not rows:
        await update.message.reply_text("📦 No products found.")
        return ConversationHandler.END

    keyboard = []

    for product_id, name, *_ in rows:
        keyboard.append([
            InlineKeyboardButton(
                name,
                callback_data=f"remove_{product_id}"
            )
        ])

    await update.message.reply_text(
        "📦 Select a product:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return REMOVE_STOCK_SELECT


async def removestock_select(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    product_id = query.data.replace("remove_", "")

    product = get_product(product_id)

    if not product:
        await query.edit_message_text("❌ Product not found.")
        return ConversationHandler.END

    context.user_data["remove_product"] = product_id

    _, name, stock = product

    await query.edit_message_text(
        f"""📦 {name}

Current Stock: {stock}

➖ How many would you like to remove?"""
    )

    return REMOVE_STOCK_AMOUNT


async def removestock_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):

    quantity = int(update.message.text)

    product_id = context.user_data["remove_product"]

    product = get_product(product_id)

    _, name, old_stock = product

    if quantity > old_stock:
        await update.message.reply_text(
            f"❌ Cannot remove {quantity}.\nOnly {old_stock} left in stock."
        )
        return REMOVE_STOCK_AMOUNT

    remove_stock(product_id, quantity)

    new_stock = old_stock - quantity

    await update.message.reply_text(
        f"""✅ Stock Updated!

📦 {name}

Old Stock: {old_stock}
Removed: {quantity}

New Stock: {new_stock}"""
    )

    return ConversationHandler.END

async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE):

    rows = get_products()

    if not rows:
        await update.message.reply_text("📦 No products found.")
        return ConversationHandler.END

    keyboard = []

    for product_id, name, *_ in rows:
        keyboard.append([
            InlineKeyboardButton(
                name,
                callback_data=f"sell_{product_id}"
            )
        ])

    await update.message.reply_text(
        "🛒 Select a product to sell:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return SELL_SELECT

async def sell_select(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    product_id = query.data.replace("sell_", "")

    product = get_product_sale(product_id)

    if not product:
        await query.edit_message_text("❌ Product not found.")
        return ConversationHandler.END

    context.user_data["sale_product"] = product_id

    _, name, cost, price, stock = product

    if stock <= 0:
        await query.edit_message_text(
            f"❌ {name} is out of stock."
        )
        return ConversationHandler.END

    await query.edit_message_text(
        f"""🛒 {name}

Current Stock: {stock}

💵 Selling Price: ${price:.2f}

How many would you like to sell?"""
    )

    return SELL_QUANTITY

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "❌ Product creation cancelled."
    )

    return ConversationHandler.END
