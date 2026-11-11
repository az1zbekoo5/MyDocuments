from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from io import BytesIO
from PIL import Image
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_H
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import (
    RoundedModuleDrawer,
    CircleModuleDrawer,
    SquareModuleDrawer
)
from qrcode.image.styles.colormasks import (
    SolidFillColorMask,
    RadialGradiantColorMask,
)
import re

TOKEN = "8529667416:AAHZ8EI1WeLZzsHc2Y6An47rOWCWZ8dfa6w"
# States
(
    MODE,
    GEN_TYPE,
    DATA,
    LOGO,
    MODULE_STYLE,
    FILL_TYPE,
    COLOR,
    CONFIRM
) = range(8)

PRESET_COLORS = {
    "black": "#000000",
    "white": "#ffffff",
    "green": "#006600",
    "yellow":"#ffff00",
    "purple": "#660099",
    "blue": "#0033cc",
    "orange": "#ff7300",
    "red": "#990000",
    "brown": "#4d382a",
      
}

COLOR_KB = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("⚫ Black", callback_data="color_black"),
        InlineKeyboardButton("⚪ White", callback_data="color_white")
    ],
    [
        InlineKeyboardButton("🟢 Green", callback_data="color_green"),
        InlineKeyboardButton("🟡 Yellow", callback_data="color_yellow")
    ],
    [
        InlineKeyboardButton("🟣 Purple", callback_data="color_purple"),
        InlineKeyboardButton("🔵 Blue", callback_data="color_blue")
    ],
    [
        InlineKeyboardButton("🟠 Orange", callback_data="color_orange"),
        InlineKeyboardButton("🔴 Red", callback_data="color_red")
    ],
    [
        InlineKeyboardButton("🟤 Brown", callback_data="color_brown"),
        InlineKeyboardButton("🎨 Custom HEX", callback_data="color_hex")
    ],
])

# ---------- UTILS ----------
def is_hex(color: str) -> bool:
    return bool(re.fullmatch(r"#([0-9a-fA-F]{6})", color))

def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    hex_str = hex_str.lstrip('#').upper()
    if len(hex_str) != 6 or not all(c in '0123456789ABCDEF' for c in hex_str):
        raise ValueError("Invalid hex")
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def generate_qr(context: ContextTypes.DEFAULT_TYPE) -> BytesIO:
    ud = context.user_data
    data = ud.get("data", "")
    if not data:
        raise ValueError("No data provided")

    # High error correction for logo, gradient, or fancy styles
    use_high = ud.get("logo") or ud.get("fill_type") == "radial" or ud.get("module_style") in ("circle", "rounded")
    qr = qrcode.QRCode(
        error_correction=ERROR_CORRECT_H if use_high else ERROR_CORRECT_L,
        box_size=28,
        border=4,
        version=1
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Module style
    drawer_map = {
        "square": SquareModuleDrawer(),
        "rounded": RoundedModuleDrawer(),
        "circle": CircleModuleDrawer(),
    }
    module_drawer = drawer_map.get(ud.get("module_style", "square"))

    # Colors
    back_rgb = hex_to_rgb(ud.get("back_color", "#0F0F0F"))
    fill_color = ud.get("fill_color", "#000000")
    edge_color = ud.get("edge_color", "#0066FF")
    if back_rgb == (0, 0, 0):
        back_rgb = (10, 10, 10)

    if ud.get("fill_type") == "radial":
        color_mask = RadialGradiantColorMask(
            back_color=back_rgb,
            center_color=hex_to_rgb(fill_color),
            edge_color=hex_to_rgb(edge_color),
        )
    else:
        color_mask = SolidFillColorMask(
            back_color=back_rgb,
            front_color=hex_to_rgb(fill_color),
        )
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=module_drawer,
        color_mask=color_mask,
    ).convert("RGBA")

    # Logo
    if logo := ud.get("logo"):
        size = img.size[0] // 5
        logo = logo.resize((size, size), Image.Resampling.LANCZOS)
        pos = ((img.size[0] - size) // 2, (img.size[1] - size) // 2)
        img.paste(logo, pos, logo)

    bio = BytesIO()
    bio.name = "QR_Code.png"
    img.save(bio, "PNG")
    bio.seek(0)
    return bio

# ---------- COLOR HELPERS ----------
async def color_prompt(update_or_query, context, title: str, target: str):
    context.user_data["color_target"] = target
    if isinstance(update_or_query, Update) and update_or_query.callback_query:
        q = update_or_query.callback_query
        await q.edit_message_text(title, reply_markup=COLOR_KB)
    elif isinstance(update_or_query, Update) and update_or_query.message:
        await update_or_query.message.reply_text(title, reply_markup=COLOR_KB)
    else:
        # callback query object
        await update_or_query.edit_message_text(title, reply_markup=COLOR_KB)
    return COLOR

async def proceed_after_color(query, context, current_target):
    fill_type = context.user_data.get("fill_type", "solid")
    if current_target == "fill" and fill_type == "radial":
        return await color_prompt(query, context, "Choose edge color:", "edge")
    elif current_target in ("fill", "edge"):
        return await color_prompt(query, context, "Choose background color:", "back")
    else:
        return await show_confirm(query, context)

# ---------- HANDLERS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("📤 Generate QR", callback_data="gen")]]
    await update.message.reply_text("Welcome! Choose action:", reply_markup=InlineKeyboardMarkup(kb))
    return MODE

async def safe_edit(
    query,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
):
    msg = query.message

    if msg.text:
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
        )
    else:
        await query.edit_message_caption(
            caption=text,
            reply_markup=reply_markup,
        )

async def choose_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    kb = [
        [InlineKeyboardButton("Simple (defaults)", callback_data="simple")],
        [InlineKeyboardButton("Custom style", callback_data="custom")],
        [InlineKeyboardButton("With logo", callback_data="logo")],
    ]
    await safe_edit(q, "Choose generation type:", InlineKeyboardMarkup(kb))

    return GEN_TYPE

async def choose_gen_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data.clear()
    context.user_data["type"] = q.data
    await safe_edit(q, "Send the content (text, URL, etc.) for the QR code:")
    return DATA

async def receive_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["data"] = update.message.text.strip()
    typ = context.user_data.get("type")

    if typ == "simple":
        context.user_data.update({
            "module_style": "square",
            "fill_type": "solid",
            "fill_color": "#000000",
            "back_color": "#FFFFFF",
            "edge_color": "#0066FF",
        })
        return await show_confirm(update, context)

    if typ == "logo":
        await update.message.reply_text("Upload your logo image (as photo):")
        return LOGO

    # custom → start styling
    return await module_style_prompt(update, context)

async def receive_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    bytes_data = await file.download_as_bytearray()
    logo_img = Image.open(BytesIO(bytes_data)).convert("RGBA")
    context.user_data["logo"] = logo_img
    return await module_style_prompt(update, context)

async def module_style_prompt(update_or_query, context):
    kb = [
        [InlineKeyboardButton("Square (classic)", callback_data="style_square")],
        [InlineKeyboardButton("Rounded", callback_data="style_rounded")],
        [InlineKeyboardButton("Circle dots", callback_data="style_circle")],
    ]
    text = "Choose module style:"
    if update_or_query.callback_query:
        await update_or_query.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb))
    else:
        await update_or_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
    return MODULE_STYLE

async def choose_module_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    style = q.data.split("_")[-1]
    context.user_data["module_style"] = style
    kb = [
        [InlineKeyboardButton("Solid color", callback_data="fill_solid")],
        [InlineKeyboardButton("Radial gradient", callback_data="fill_radial")],
    ]
    await safe_edit(q, "Choose fill type:", reply_markup=InlineKeyboardMarkup(kb))
    return FILL_TYPE

async def choose_fill_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    fill_type = q.data.split("_")[-1]
    context.user_data["fill_type"] = fill_type
    if fill_type == "solid":
        title = "Choose solid fill color:"
        target = "fill"
    else:
        title = "Choose center color (main color):"
        target = "fill"
    return await color_prompt(q, context, title, target)

async def choose_preset_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    color_key = q.data.replace("color_", "")
    color = PRESET_COLORS.get(color_key, "#000000")
    target = context.user_data.pop("color_target", "fill")
    if target == "fill":
        context.user_data["fill_color"] = color
    elif target == "edge":
        context.user_data["edge_color"] = color
    elif target == "back":
        context.user_data["back_color"] = color
    return await proceed_after_color(q, context, target)

async def choose_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    # Only responsible for switching to HEX input
    if q.data == "color_hex":
        await safe_edit(q, "Send HEX color (example: #3366FF):")
        return COLOR

    # Safety fallback (should never happen)
    return COLOR


async def receive_hex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    color = update.message.text.strip().upper()
    if not is_hex(color):
        await update.message.reply_text("Invalid HEX (e.g. #3366FF). Try again:")
        return COLOR
    target = context.user_data.pop("color_target", "fill")
    if target == "fill":
        context.user_data["fill_color"] = color
    elif target == "edge":
        context.user_data["edge_color"] = color
    elif target == "back":
        context.user_data["back_color"] = color

    fill_type = context.user_data.get("fill_type", "solid")
    if target == "fill" and fill_type == "radial":
        await update.message.reply_text("Choose edge color:", reply_markup=COLOR_KB)
        context.user_data["color_target"] = "edge"
        return COLOR
    elif target in ("fill", "edge"):
        await update.message.reply_text("Choose background color:", reply_markup=COLOR_KB)
        context.user_data["color_target"] = "back"
        return COLOR
    else:
        return await show_confirm(update, context)

async def show_confirm(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    if isinstance(update_or_query, Update):
        message = update_or_query.message
    else:  # CallbackQuery
        message = update_or_query.message

    ud = context.user_data
    ft = ud.get("fill_type", "solid")

    text = (
        "Confirm your styled QR:\n\n"
        f"• Content: {ud.get('data', '—')}\n"
        f"• Module:  {ud.get('module_style', 'square').title()}\n"
        f"• Fill:    {ft.title()}\n"
    )

    if ft == "radial":
        text += f"  ├ Center: {ud.get('fill_color', '#000000')}\n"
        text += f"  └ Edge:   {ud.get('edge_color', '#0066FF')}\n"
    else:
        text += f"  └ Color:  {ud.get('fill_color', '#000000')}\n"

    text += f"• Background: {ud.get('back_color', '#FFFFFF')}\n"
    text += f"• Logo:       {'Yes' if ud.get('logo') else 'No'}\n"

    kb = [
        [InlineKeyboardButton("✅ Generate", callback_data="generate")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
    ]

    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
    return CONFIRM


async def handle_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "cancel":
        await safe_edit(q, "Cancelled.")
        context.user_data.clear()
        return ConversationHandler.END
    
    try:
        bio = generate_qr(context)
        kb = [[InlineKeyboardButton("📤 Generate QR", callback_data="gen")]]
        await q.message.reply_document(document=bio, caption="Your custom QR code ✨\nScan it!", reply_markup=InlineKeyboardMarkup(kb))
        return MODE
    
    except Exception as e:
        await q.message.reply_text(f"Error generating QR: {e}")

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END

# ---------- MAIN ----------
def main():
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MODE: [CallbackQueryHandler(choose_mode, pattern="^gen$")],
            GEN_TYPE: [CallbackQueryHandler(choose_gen_type)],
            DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_data)],
            LOGO: [MessageHandler(filters.PHOTO, receive_logo)],
            MODULE_STYLE: [CallbackQueryHandler(choose_module_style, pattern="^style_")],
            FILL_TYPE: [CallbackQueryHandler(choose_fill_type, pattern="^fill_")],
            COLOR: [
                CallbackQueryHandler(choose_color, pattern="^color_hex$"),
                CallbackQueryHandler(choose_preset_color, pattern="^color_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_hex),
            ],
            CONFIRM: [
                CallbackQueryHandler(choose_mode, pattern="^gen$"),
                CallbackQueryHandler(handle_confirm, pattern="^(generate|cancel)$")],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CallbackQueryHandler(handle_confirm, pattern="^cancel$"),
        ],
        allow_reentry=True,
    )

    app.add_handler(conv)
    print("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()