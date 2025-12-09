import os, time
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ChatMember
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from db import *

# CONFIG =============================
TOKEN = "8168498060:AAEq5jx_dDVrqWxukCmux4Lzha5CKk7aAY4"
ADMIN_IDS = ["8583137173"]

CHANNELS = [
    "@otp_z0ne",
    "@Alexx_network",
    "@foxsmsshop",
    "@vtkqo",
    "@JMB_CODER"
]

YOUTUBE_URL = "https://youtube.com/@bizzle.editor?si=mEQc23KfQssp8nJJ"

app = Flask(__name__)
init_db()

user_youtube = {}


def make_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join 1", url="https://t.me/otp_z0ne")],
        [InlineKeyboardButton("📢 Join 2", url="https://t.me/Alexx_network")],
        [InlineKeyboardButton("📢 Join 3", url="https://t.me/foxsmsshop")],
        [InlineKeyboardButton("📢 Join 4", url="https://t.me/vtkqo")],
        [InlineKeyboardButton("📢 Join 5", url="https://t.me/JMB_CODER")],
        [InlineKeyboardButton("▶️ YouTube", url=YOUTUBE_URL)],
        [InlineKeyboardButton("👍 I Subscribed YouTube", callback_data="yt_done")],
        [InlineKeyboardButton("🔁 Verify All", callback_data="verify")],
        [InlineKeyboardButton("💰 Wallet", callback_data="wallet")],
        [InlineKeyboardButton("📣 Referral Link", callback_data="ref")],
        [InlineKeyboardButton("💵 Withdraw", callback_data="withdraw")],
    ])


def check_channels(user_id, context):
    for ch in CHANNELS:
        try:
            m = context.bot.get_chat_member(ch, user_id)
            if m.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True


def start(update, context):
    chat_id = update.effective_chat.id
    args = context.args

    referred_by = None
    if args and args[0].startswith("REF_"):
        referred_by = args[0].replace("REF_", "")
        if referred_by == str(chat_id):
            referred_by = None

    create_user(chat_id, referred_by)

    context.bot.send_message(
        chat_id,
        "🔥 Welcome to Referral Bot!\nComplete steps & earn ₹10 per referral!",
        reply_markup=make_keyboard()
    )


def button(update, context):
    q = update.callback_query
    user = q.from_user
    chat_id = q.message.chat.id
    q.answer()

    data = q.data

    if data == "yt_done":
        user_youtube[user.id] = True
        context.bot.send_message(chat_id, "✅ YouTube Confirmed!")

    elif data == "verify":
        channels_ok = check_channels(user.id, context)
        yt_ok = user_youtube.get(user.id, False)

        if channels_ok and yt_ok:
            row = get_user(user.id)
            if row and row[2] == 0:
                mark_verified(user.id)
                if row[1]:
                    credit_referral(row[1])

            context.bot.send_message(chat_id, "🎉 Verified! Earned ₹10 to referrer!")
        else:
            context.bot.send_message(chat_id, "❌ Complete all steps first!")

    elif data == "wallet":
        b = get_balance(user.id)
        context.bot.send_message(chat_id, f"💰 Balance: ₹{b}")

    elif data == "ref":
        link = f"https://t.me/{context.bot.username}?start=REF_{user.id}"
        context.bot.send_message(chat_id, f"📣 Share & Earn ₹10:\n\n{link}")

    elif data == "withdraw":
        b = get_balance(user.id)
        if b < 100:
            context.bot.send_message(chat_id, "❌ Minimum ₹100 required!")
            return
        context.bot.send_message(chat_id, "Send UPI ID:")
        context.user_data["awaiting_upi"] = True

    elif data.startswith("approve_"):
        wid = data.replace("approve_", "")
        approve_withdraw(wid)
        context.bot.send_message(chat_id, "Approved!")
        return

    elif data.startswith("reject_"):
        wid = data.replace("reject_", "")
        reject_withdraw(wid)
        context.bot.send_message(chat_id, "Rejected!")
        return


def message_handler(update, context):
    user_id = update.effective_chat.id
    if context.user_data.get("awaiting_upi"):
        upi = update.message.text
        amt = get_balance(user_id)
        create_withdraw(user_id, amt, upi)

        for admin in ADMIN_IDS:
            context.bot.send_message(
                admin,
                f"🔔 Withdraw Request\nUser: {user_id}\nAmount: ₹{amt}\nUPI: {upi}\n\nApprove?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Approve", callback_data=f"approve_{user_id}"),
                     InlineKeyboardButton("Reject", callback_data=f"reject_{user_id}")]
                ])
            )

        context.user_data["awaiting_upi"] = False
        context.bot.send_message(user_id, "⌛ Waiting for approval!")


def setup():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler("admin", admin_panel))
    dp.add_handler(MessageHandler(None, message_handler, pass_user_data=True))

    return updater


def admin_panel(update, context):
    chat_id = update.effective_chat.id
    if str(chat_id) not in ADMIN_IDS:
        return

    rows = list_pending_withdrawals()
    if not rows:
        context.bot.send_message(chat_id, "No pending withdrawals.")
        return

    for row in rows:
        wid, user_id, amount, upi = row
        context.bot.send_message(
            chat_id,
            f"Pending:\nUser: {user_id}\nAmount: ₹{amount}\nUPI: {upi}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Approve", callback_data=f"approve_{wid}"),
                 InlineKeyboardButton("Reject", callback_data=f"reject_{wid}")]
            ])
        )


dispatcher = setup()

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, dispatcher.bot)
    dispatcher.process_update(update)
    return "ok"


@app.route("/")
def home():
    return "Bot running"


if __name__ == "__main__":
    app.run(port=5000)
