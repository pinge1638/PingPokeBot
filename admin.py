from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes

import config
from database import get_orders_by_status

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Owner only
    if update.effective_user.id != config.OWNER_ID:
        await update.message.reply_text(
            "⛔ You are not allowed to use this command."
        )
        return

    keyboard = [
        [
            InlineKeyboardButton("📦 Inventory", callback_data="inventory")
        ],
        [
            InlineKeyboardButton("🛒 Orders", callback_data="orders")
        ],
        [
            InlineKeyboardButton("🚢 Pre Orders", callback_data="preorders")
        ],
        [
            InlineKeyboardButton("💳 Payments", callback_data="payments")
        ],
        [
            InlineKeyboardButton("🎁 Giveaway", callback_data="giveaway")
        ],
        [
            InlineKeyboardButton("📊 Reports", callback_data="reports")
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="settings")
        ],
    ]

    await update.message.reply_text(
        "🛠 **PingPoke Admin Panel**\n\n"
        "Select a module below.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )

# ======================================
# CALLBACK BUTTONS
# ======================================

async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "inventory":

        keyboard = [
            [InlineKeyboardButton("➕ Add Product", callback_data="add_product")],
            [InlineKeyboardButton("📋 View Products", callback_data="view_products")],
            [InlineKeyboardButton("✏️ Edit Product", callback_data="edit_product")],
            [InlineKeyboardButton("➕ Add Stock", callback_data="add_stock")],
            [InlineKeyboardButton("➖ Deduct Stock", callback_data="deduct_stock")],
            [InlineKeyboardButton("🗑 Hide Product", callback_data="hide_product")],
            [InlineKeyboardButton("⬅ Back", callback_data="back_admin")],
        ]
    
        await query.edit_message_text(
            "📦 *Inventory Management*\n\nChoose an option.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )
    
    
    elif query.data == "orders":
    
        pending = get_orders_by_status("Pending Verification")
        approved = get_orders_by_status("Approved")
        rejected = get_orders_by_status("Rejected")
    
        keyboard = [
            [
                InlineKeyboardButton(
                    f"🟡 Pending Verification ({len(pending)})",
                    callback_data="orders_pending",
                )
            ],
            [
                InlineKeyboardButton(
                    f"🟢 Approved ({len(approved)})",
                    callback_data="orders_approved",
                )
            ],
            [
                InlineKeyboardButton(
                    f"🔴 Rejected ({len(rejected)})",
                    callback_data="orders_rejected",
                )
            ],
            [
                InlineKeyboardButton(
                    "⬅ Back",
                    callback_data="back_admin",
                )
            ],
        ]
    
        await query.edit_message_text(
            "🛒 *Order Management*\n\n"
            "Choose an order status.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )
    
    elif query.data == "orders_pending":

        orders = get_orders_by_status("Pending Verification")
    
        if not orders:
            await query.edit_message_text(
                "🟡 *Pending Verification*\n\n"
                "No pending orders.",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "⬅ Back",
                            callback_data="orders",
                        )
                    ]
                ]),
                parse_mode="Markdown",
            )
            return
    
        keyboard = []
    
        for order in orders:
    
            order_number = order[0]
            username = order[2]
            total = order[6]
    
            keyboard.append([
                InlineKeyboardButton(
                    f"🟡 #{order_number} • @{username} • ${total:.2f}",
                    callback_data=f"vieworder_{order_number}",
                )
            ])
    
        keyboard.append([
            InlineKeyboardButton(
                "⬅ Back",
                callback_data="orders",
            )
        ])
    
        await query.edit_message_text(
            "🟡 *Pending Verification*\n\n"
            "Select an order:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    elif query.data == "orders_approved":

        orders = get_orders_by_status("Approved")
    
        if not orders:
            await query.edit_message_text(
                "🟢 *Approved Orders*\n\n"
                "No approved orders.",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "⬅ Back",
                            callback_data="orders",
                        )
                    ]
                ]),
                parse_mode="Markdown",
            )
            return
    
        keyboard = []
    
        for order in orders:
    
            order_number = order[0]
            username = order[2]
            total = order[6]
    
            keyboard.append([
                InlineKeyboardButton(
                    f"🟢 #{order_number} • @{username} • ${total:.2f}",
                    callback_data=f"vieworder_{order_number}",
                )
            ])
    
        keyboard.append([
            InlineKeyboardButton(
                "⬅ Back",
                callback_data="orders",
            )
        ])
    
        await query.edit_message_text(
            "🟢 *Approved Orders*\n\n"
            "Select an order:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    elif query.data == "orders_rejected":

        orders = get_orders_by_status("Rejected")
    
        if not orders:
            await query.edit_message_text(
                "🔴 *Rejected Orders*\n\n"
                "No rejected orders.",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "⬅ Back",
                            callback_data="orders",
                        )
                    ]
                ]),
                parse_mode="Markdown",
            )
            return
    
        keyboard = []
    
        for order in orders:
    
            order_number = order[0]
            username = order[2]
            total = order[6]
    
            keyboard.append([
                InlineKeyboardButton(
                    f"🔴 #{order_number} • @{username} • ${total:.2f}",
                    callback_data=f"vieworder_{order_number}",
                )
            ])
    
        keyboard.append([
            InlineKeyboardButton(
                "⬅ Back",
                callback_data="orders",
            )
        ])

        await query.edit_message_text(
            "🔴 *Rejected Orders*\n\n"
            "Select an order:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )
    
    elif query.data == "back_admin":
    
        keyboard = [
            [InlineKeyboardButton("📦 Inventory", callback_data="inventory")],
            [InlineKeyboardButton("🛒 Orders", callback_data="orders")],
            [InlineKeyboardButton("🚢 Pre Orders", callback_data="preorders")],
            [InlineKeyboardButton("💳 Payments", callback_data="payments")],
            [InlineKeyboardButton("🎁 Giveaway", callback_data="giveaway")],
            [InlineKeyboardButton("📊 Reports", callback_data="reports")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
        ]
    
        await query.edit_message_text(
            "🛠 *PingPoke Admin Panel*\n\n"
            "Select a module below.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )
