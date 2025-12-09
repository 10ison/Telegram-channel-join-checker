import sys
import types

# fix imghdr error for Python 3.13
fake_imghdr = types.ModuleType("imghdr")
sys.modules["imghdr"] = fake_imghdr

from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

TOKEN = "8168498060:AAEq5jx_dDVrqWxukCmux4Lzha5CKk7aAY4"
CHANNELS = [
    "https://t.me/otp_z0ne",
    "https://t.me/Alexx_network",
    "https://t.me/foxsmsshop",
    "https://t.me/vtkqo",
    "https://t.me/JMB_CODER",
]
YOUTUBE = "https://youtube.com/@bizzle.editor"

WEB_URL = "https://telegram-channel-join-checker.onrender.com"

app = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("🔗 Join Channels", callback_data="join")],
        [InlineKeyboardButton("📺 Subscribe YouTube", url=YOUTUBE)],
        [InlineKeyboardButton("✔️ Verify", callback_data="verify")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        "👋 Welcome!\n\nJoin all channels + subscribe YouTube then click Verify.",
        reply_markup=reply_markup
    )


async def join_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "👇 Join all channels:\n\n"
    for c in CHANNELS:
        text += f"🔗 {c}\n"

    await update.callback_query.message.reply_text(text)


async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # real check here
    await update.callback_query.message.reply_text(
        "⏳ Checking...\n\n✔️ Verified! 🎉"
    )


bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(join_channels, pattern="join"))
bot_app.add_handler(CallbackQueryHandler(verify, pattern="verify"))


@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    bot_app.update_queue.put(request.json)
    return "ok"


@app.route("/")
def home():
    return "Bot is running!"


if __name__ == "__main__":
    bot_app.run_webhook(
        listen="0.0.0.0",
        port=10000,
        url_path=TOKEN,
        webhook_url=f"{WEB_URL}/{TOKEN}"
    )
