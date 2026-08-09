from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    ContextTypes,
)

from database import (
    add_to_cart,
    get_cart,
    get_cart_quantity,
    create_order,
    clear_cart,
    increase_cart,
    decrease_cart,
    remove_cart_item,
)

from google_sheets import get_products

SELECT_QUANTITY = 0

def get_product_details(product_id):
    products = get_products()

    for product in products:
        if product["product_id"] == product_id:
            return (
                product["product_id"],
                product["name"],
                product["category"],
                product["type"],
                product["cost"],
                product["price"],
                product["stock"],
            )

    return None

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
    
    context.user_data["shop_product_type"] = product_type

    category = context.user_data["shop_category"]

    products = get_products()

    keyboard = []
    
    for product in products:
    
        product_id = product["product_id"]
        name = product["name"]
        cat = product["category"]
        ptype = product["type"]
        price = product["price"]
        stock = product["stock"]
    
        if cat != category:
            continue
    
        if ptype != product_type:
            continue
    
        if stock <= 0:
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
    
    keyboard.append([
        InlineKeyboardButton(
            "⬅️ Back",
            callback_data="back_shop_type",
        )
    ])
    
    await query.edit_message_text(
        f"📦 {category}\n{product_type}\n\nChoose a product:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def back_to_shop_type(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    category = context.user_data.get("shop_category")

    if not category:
        await query.edit_message_text(
            "❌ Unable to return."
        )
        return

    keyboard = [
        [
            InlineKeyboardButton(
                "📦 Ready Stock",
                callback_data="shop_ready",
            )
        ],
        [
            InlineKeyboardButton(
                "🚢 Preorder",
                callback_data="shop_preorder",
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="shop_back_category",
            )
        ],
    ]

    await query.edit_message_text(
        f"📂 {category}\n\n"
        "Choose Product Type",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def back_to_products(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    category = context.user_data.get("shop_category")
    product_type = context.user_data.get("shop_product_type")

    if not category or not product_type:
        await query.edit_message_text(
            "❌ Unable to return to products."
        )
        return

    products = get_products()

    keyboard = []
    
    for product in products:
    
        product_id = product["product_id"]
        name = product["name"]
        cat = product["category"]
        ptype = product["type"]
        price = product["price"]
        stock = product["stock"]
    
        if cat != category:
            continue
    
        if ptype != product_type:
            continue
    
        if stock <= 0:
            continue
    
        keyboard.append([
            InlineKeyboardButton(
                f"{name} • ${price:.2f} • Stock {stock}",
                callback_data=f"product_{product_id}"
            )
        ])

    if not keyboard:
        await query.edit_message_text(
            f"📦 {category}\n{product_type}\n\n"
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
  
    keyboard = []
    row = []

    for i in range(1, stock + 1):
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
    
    📦 Stock: {stock}
    
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
        ],
        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="back_products",
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

    product = get_product_details(product_id)

    if not product:
        await query.answer(
            "❌ Product not found.",
            show_alert=True,
        )
        return

    stock = product[6]

    current_cart_qty = get_cart_quantity(
        query.from_user.id,
        product_id,
    )

    remaining = stock - current_cart_qty

    if qty > remaining:
        await query.answer(
            f"❌ You can only add {remaining} more.",
            show_alert=True,
        )
        return

    add_to_cart(
        query.from_user.id,
        product_id,
        qty,
    )

    await show_cart(query)

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

async def show_cart(query):

    cart = get_cart(query.from_user.id)

    text = "🛒 Your Cart\n\n"

    total = 0
    keyboard = []

    for product_id, name, old_price, qty in cart:

        product = get_product_details(product_id)

        if not product:
            continue

        current_price = product[5]

        subtotal = current_price * qty
        total += subtotal

        text += (
            f"📦 {name}\n"
            f"x{qty} • ${subtotal:.2f}\n\n"
        )

        keyboard.append([
            InlineKeyboardButton(
                "➖",
                callback_data=f"minus_{product_id}",
            ),
            InlineKeyboardButton(
                "➕",
                callback_data=f"plus_{product_id}",
            ),
            InlineKeyboardButton(
                "🗑",
                callback_data=f"delete_{product_id}",
            ),
        ])

    text += f"💰 Total: ${total:.2f}"

    keyboard.append([
        InlineKeyboardButton(
            "🛍 Continue Shopping",
            callback_data="continue_shop",
        )
    ])

    keyboard.append([
        InlineKeyboardButton(
            "💳 Checkout",
            callback_data="checkout",
        )
    ])

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def show_cart(query):

    cart = get_cart(query.from_user.id)

    text = "🛒 Your Cart\n\n"

    total = 0
    keyboard = []

    for product_id, name, old_price, qty in cart:

        product = get_product_details(product_id)

        if not product:
            continue

        current_price = product[5]

        subtotal = current_price * qty
        total += subtotal

        text += (
            f"📦 {name}\n"
            f"x{qty} • ${subtotal:.2f}\n\n"
        )

        keyboard.append([
            InlineKeyboardButton(
                "➖",
                callback_data=f"minus_{product_id}",
            ),
            InlineKeyboardButton(
                "➕",
                callback_data=f"plus_{product_id}",
            ),
            InlineKeyboardButton(
                "🗑",
                callback_data=f"delete_{product_id}",
            ),
        ])

    text += f"💰 Total: ${total:.2f}"

    keyboard.append([
        InlineKeyboardButton(
            "🛍 Continue Shopping",
            callback_data="continue_shop",
        )
    ])

    keyboard.append([
        InlineKeyboardButton(
            "💳 Checkout",
            callback_data="checkout",
        )
    ])

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def plus_item(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    product_id = query.data.replace("plus_", "")

    product = get_product_details(product_id)

    if not product:
        await query.answer(
            "❌ Product not found.",
            show_alert=True,
        )
        return

    stock = product[6]

    cart_qty = get_cart_quantity(
        query.from_user.id,
        product_id,
    )

    if cart_qty >= stock:
        await query.answer(
            f"❌ Maximum stock reached: {stock}",
            show_alert=True,
        )
        return

    increase_cart(
        query.from_user.id,
        product_id,
    )

    await show_cart(query)


async def minus_item(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    product_id = query.data.replace("minus_", "")

    decrease_cart(
        query.from_user.id,
        product_id,
    )

    await show_cart(query)


async def delete_item(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    product_id = query.data.replace("delete_", "")

    remove_cart_item(
        query.from_user.id,
        product_id,
    )

    await show_cart(query)


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

    for product_id, name, old_price, qty in cart:

        product = get_product_details(product_id)
    
        if not product:
            continue
    
        current_price = product[5]
    
        line_total = current_price * qty
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

async def back_cart(update, context):

    query = update.callback_query
    await query.answer()

    await show_cart(query)

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

    for product_id, name, old_price, qty in cart:

        product = get_product_details(product_id)
    
        if not product:
            continue
    
        current_price = product[5]
    
        items += f"{name} x{qty}\n"
        subtotal += current_price * qty

    shipping = context.user_data["shipping"]
    delivery = context.user_data["delivery"]

    total = subtotal + shipping

    order_number = create_order(
        update.effective_user.id,
        update.effective_user.username,
        cart,
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

    from config import OWNER_ID

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Approve",
                callback_data=f"approve_{order_number}",
            ),
            InlineKeyboardButton(
                "❌ Reject",
                callback_data=f"reject_{order_number}",
            ),
        ]
    ]

    await context.bot.send_photo(
        chat_id=OWNER_ID,
        photo=photo.file_id,
        caption=f"""
    🛒 NEW ORDER
    
    Order #{order_number}
    
    Customer:
    @{update.effective_user.username}
    
    Items:
    {items}
    
    Subtotal: ${subtotal:.2f}
    Shipping: ${shipping:.2f}
    Total: ${total:.2f}
    
    Delivery:
    {delivery}
    """,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    clear_cart(update.effective_user.id)
    return ConversationHandler.END
