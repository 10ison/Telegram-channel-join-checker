from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)
from db import init_db, add_user, add_balance, get_balance
import requests, threading, asyncio

# ---------------- CONFIG ----------------

BOT_TOKEN = "YOUR_TOKEN"   # CHANGE
ADMIN_ID = 8583137173      # YOU CONFIRMED
MIN_WITHDRAW = 100

CHANNELS = [
    "https://t.me/JMB_CODER",
    "https://t.me/otp_z0ne",
    "https://t.me/Alexx_network",
    "https://t.me/foxsmsshop",
    "https://t.me/vtkqo"
]

YOUTUBE = "https://youtube.com/@bizzle.editor"

# ---------------- KEEP ALIVE ----------------

def auto_ping():
    try:
        requests.get("https://telegram-channel-join-checker.onrender.com/") # CHANGE URL
    except:
        pass
    threading.Timer(240, auto_ping).start()

auto_ping()

# ---------------- DB INIT ----------------

init_db()

# ---------------- FLASK APP ----------------

app = Flask(__name__)

@app.route("/")
def home():
    return "BOT RUNNING"

# ---------------- TELEGRAM BOT ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    args = context.args

    ref = None
    if args:
        ref = args[0]

    add_user(uid, ref)

    btns = [
        [InlineKeyboardButton("📢 Join Channels", callback_data="join")],
        [InlineKeyboardButton("🎬 Subscribe", url=YOUTUBE)],
        [InlineKeyboardButton("✔️ Verify", callback_data="verify")],
        [InlineKeyboardButton("💰 Wallet", callback_data="wallet")],
        [InlineKeyboardButton("👥 Referral", callback_data="ref")]
    ]

    await update.message.reply_text(
        "🔥 Welcome! Earn ₹10 per referral!",
        reply_markup=InlineKeyboardMarkup(btns)
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id

    if q.data == "join":
        txt = "👇 Join all channels:\n\n"
        for c in CHANNELS:
            txt += f"🔗 {c}\n"
        await q.message.edit_text(txt)

    elif q.data == "verify":
        add_balance(uid, 10)
        await q.message.edit_text("🎉 Verified! +₹10 added!")

    elif q.data == "wallet":
        bal = get_balance(uid)
        await q.message.edit_text(f"💰 Your Balance: ₹{bal}")

    elif q.data == "ref":
        link = f"https://t.me/{context.bot.username}?start={uid}"
        await q.message.edit_text(f"👥 Share your link:\n{link}")

# ---------------- BOOT BOT ----------------

async def run_bot():
    bot = ApplicationBuilder().token(BOT_TOKEN).build()

    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(CallbackQueryHandler(button))

    await bot.start()
    await bot.updater.start_polling()
    await bot.updater.idle()

import threading
threading.Thread(target=lambda: asyncio.run(run_bot())).start()

app.run(host="0.0.0.0", port=10000)
