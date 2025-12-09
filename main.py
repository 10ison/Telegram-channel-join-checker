import sys
import types
import logging
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ChatMember
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram.ext import Dispatcher
import os

# ---------------- FIX FOR PYTHON 3.13 ----------------
fake_imghdr = types.ModuleType("imghdr")
sys.modules["imghdr"] = fake_imghdr
# -----------------------------------------------------

TELEGRAM_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Channels / YouTube
CHANNELS = [
    "https://t.me/otp_z0ne",
    "https://t.me/Alexx_network",
    "https://t.me/foxsmsshop",
    "https://t.me/vtkqo",
    "https://t.me/JMB_CODER",
]
YOUTUBE_URL = "https://youtube.com/@bizzle.editor"

# Flask server
app = Flask(__name__)

# Logger
logging.basicConfig(level=logging.INFO)


# ---------------- TELEGRAM BOT START ----------------

def start(update: Update, context):
    keyboard = []

    for ch in CHANNELS:
        keyboard.append([InlineKeyboardButton("Join Channel", url=ch)])

    keyboard.append([InlineKeyboardButton("Subscribe YouTube", url=YOUTUBE_URL)])
    keyboard.append([InlineKeyboardButton("Verify ✔️", callback_data="verify")])

    update.message.reply_text(
        "👇 Please join channels & subscribe then click verify",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def verify(update: Update, context):
    user = update.effective_user

    # Simple fake check (you can add real join check if admin rights)
    update.callback_query.answer("Checking...")

    update.callback_query.edit_message_text(
        f"🎉 Verified! Welcome {user.first_name}\n\n💸 Earn Rs 10 per referral!"
    )


# ---------------- FLASK WEBHOOK ----------------

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), updater.bot)
    dispatcher.process_update(update)
    return "ok"


@app.route("/")
def home():
    return "BOT IS RUNNING!"


# ---------------- MAIN ----------------

updater = Updater(TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(verify))


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)
