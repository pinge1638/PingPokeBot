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
    add_to_cart,
    get_cart,
    get_cart_quantity,
    create_order,
)

SELECT_QUANTITY = 0

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

        available = stock - get_cart_quantity(
            query.from_user.id,
            product_id,
        )
        
        if available <= 0:
            continue
        
        keyboard.append([
            InlineKeyboardButton(
                f"{name} • ${price:.2f} • Stock {available}",
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
    cart_qty = get_cart_quantity(
    query.from_user.id,
    product_id,
)

    remaining = stock - cart_qty
    
    if remaining <= 0:
        await query.edit_message_text(
            "❌ This item is already fully reserved in your cart."
        )
        return

    keyboard = []
    row = []

    for i in range(1, remaining + 1):
        row.append(
            InlineKeyboardButton(
                str(i),
                callback_data=f"qty_{i}",
            )
        )

        if len(row) == 5:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    await query.edit_message_text(
        f"""📦 {name}

    💰 Price: ${price:.2f}
    
    📦 Available: {remaining}
    
    Choose quantity.""",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def choose_quantity(update, context):

    query = update.callback_query
    await query.answer()

    qty = int(query.data.replace("qty_", ""))

    context.user_data["selected_quantity"] = qty

    keyboard = [
        [
            InlineKeyboardButton(
                "🛒 Add to Cart",
                callback_data="cart_add",
            )
        ]
    ]

    await query.edit_message_text(
        f"""
📦 Quantity Selected

Quantity: {qty}

Press Add to Cart.
""",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def add_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    product_id = context.user_data["selected_product"]

    qty = context.user_data["selected_quantity"]

    success = add_to_cart(
        query.from_user.id,
        product_id,
        qty,
    )

    if not success:
        await query.answer(
            "Not enough stock available.",
            show_alert=True,
        )
        return

    cart = get_cart(query.from_user.id)

    text = "🛒 Your Cart\n\n"

    total = 0

    for _, name, price, qty in cart:
        subtotal = price * qty
        total += subtotal

        text += (
            f"📦 {name}\n"
            f"x{qty} • ${subtotal:.2f}\n\n"
        )

    text += f"💰 Total: ${total:.2f}"

    keyboard = [
        [
            InlineKeyboardButton(
                "🛍 Continue Shopping",
                callback_data="continue_shop",
            )
        ],
        [
            InlineKeyboardButton(
                "💳 Checkout",
                callback_data="checkout",
            )
        ],
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def continue_shop(update, context):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🟡 Pokémon", callback_data="shop_pokemon")],
        [InlineKeyboardButton("🏴‍☠️ One Piece", callback_data="shop_onepiece")],
        [InlineKeyboardButton("🎁 Accessories", callback_data="shop_accessories")],
    ]

    await query.edit_message_text(
        "🛍 Welcome to PingPoke!\n\nChoose a category.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                "🏠 Self Collection",
                callback_data="delivery_self",
            )
        ],
        [
            InlineKeyboardButton(
                "📮 Tracked Mail (+$3.50)",
                callback_data="delivery_mail",
            )
        ],
    ]

    await query.edit_message_text(
        "🚚 Choose your delivery method.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def delivery_method(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "delivery_self":
        context.user_data["delivery"] = "Self Collection"
        shipping = 0

    else:
        context.user_data["delivery"] = "Tracked Mail"
        shipping = 3.50

    context.user_data["shipping"] = shipping
    
    cart = get_cart(query.from_user.id)

    text = "📋 Order Summary\n\n"

    subtotal = 0

    for _, name, price, qty in cart:

        line_total = price * qty
        subtotal += line_total

        text += (
            f"📦 {name}\n"
            f"x{qty} • ${line_total:.2f}\n\n"
        )

    total = subtotal + shipping

    text += (
        "──────────────\n"
        f"Subtotal: ${subtotal:.2f}\n"
        f"Delivery: {context.user_data['delivery']}\n"
        f"Shipping: ${shipping:.2f}\n\n"
        f"💰 Total: ${total:.2f}"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "💳 PayNow",
                callback_data="paynow",
            )
        ],
        [
            InlineKeyboardButton(
                "🛒 Back to Cart",
                callback_data="back_cart",
            )
        ],
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def back_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    cart = get_cart(query.from_user.id)

    text = "🛒 Your Cart\n\n"

    total = 0

    for _, name, price, qty in cart:

        subtotal = price * qty
        total += subtotal

        text += (
            f"📦 {name}\n"
            f"x{qty} • ${subtotal:.2f}\n\n"
        )

    text += f"💰 Total: ${total:.2f}"

    keyboard = [
        [
            InlineKeyboardButton(
                "🛍 Continue Shopping",
                callback_data="continue_shop",
            )
        ],
        [
            InlineKeyboardButton(
                "💳 Checkout",
                callback_data="checkout",
            )
        ],
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def paynow(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    text = """
💳 PayNow Payment

Please make payment using the QR Code.

⚠️ IMPORTANT

Please screenshot your payment after transferring.

You will need to upload the screenshot on the next page.

After payment, press:

✅ I've Paid
"""

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ I've Paid",
                callback_data="paid",
            )
        ]
    ]

    await query.message.reply_photo(
        photo=open("paynow.png", "rb"),
        caption=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

from telegram.ext import ConversationHandler

WAIT_PAYMENT = 1

async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "📷 Please upload your payment screenshot.\n\n"
        "Once uploaded, our team will verify your payment."
    )

    return WAIT_PAYMENT

async def payment_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.photo:
        await update.message.reply_text(
            "❌ Please upload an image."
        )
        return WAIT_PAYMENT

    photo = update.message.photo[-1]

    context.user_data["payment_photo"] = photo.file_id

    cart = get_cart(update.effective_user.id)

    items = ""

    subtotal = 0

    for _, name, price, qty in cart:
        items += f"{name} x{qty}\n"
        subtotal += price * qty

    shipping = context.user_data["shipping"]
    delivery = context.user_data["delivery"]

    total = subtotal + shipping

    order_number = create_order(
        update.effective_user.id,
        update.effective_user.username,
        items,
        subtotal,
        shipping,
        total,
        delivery,
    )

    await update.message.reply_text(
        f"""
✅ Payment screenshot received!

Order #{order_number}

Your order has been submitted for verification.

We will notify you once payment has been confirmed.
"""
    )

    return ConversationHandler.END
