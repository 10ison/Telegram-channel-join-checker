import time
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ChatMember
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from db import *

# ================= CONFIG ====================

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


# ================= UI ====================

def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join 1", url="https://t.me/otp_z0ne")],
        [InlineKeyboardButton("📢 Join 2", url="https://t.me/Alexx_network")],
        [InlineKeyboardButton("📢 Join 3", url="https://t.me/foxsmsshop")],
        [InlineKeyboardButton("📢 Join 4", url="https://t.me/vtkqo")],
        [InlineKeyboardButton("📢 Join 5", url="https://t.me/JMB_CODER")],
        [InlineKeyboardButton("▶️ YouTube", url=YOUTUBE_URL)],
        [InlineKeyboardButton("👍 I Subscribed YouTube", callback_data="yt")],
        [InlineKeyboardButton("🔁 Verify", callback_data="verify")],
        [InlineKeyboardButton("💰 Wallet", callback_data="wallet")],
        [InlineKeyboardButton("📣 Referral", callback_data="ref")],
        [InlineKeyboardButton("💵 Withdraw", callback_data="withdraw")]
    ])


# ================= CHECK ====================

def joined_all(uid, bot):
    for ch in CHANNELS:
        try:
            m = bot.get_chat_member(ch, uid)
            if m.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True


# ================= HANDLERS ====================

def start(update, context):
    uid = update.effective_chat.id
    args = context.args

    ref = None
    if args and args[0].startswith("REF_"):
        ref = args[0].replace("REF_", "")
        if ref == str(uid):
            ref = None

    create_user(uid, ref)

    update.message.reply_text("🔥 Welcome!", reply_markup=menu())


def callback(update, context):
    q = update.callback_query
    uid = q.from_user.id
    q.answer()

    if q.data == "yt":
        user_youtube[uid] = True
        q.message.reply_text("👍 YouTube Done!")
        return

    if q.data == "verify":
        if joined_all(uid, context.bot) and user_youtube.get(uid, False):
            row = get_user(uid)
            if row and row[2] == 0:
                mark_verified(uid)
                if row[1]:
                    credit_referral(row[1])

            q.message.reply_text("🎉 Verified!")
        else:
            q.message.reply_text("❌ Complete all steps!")
        return

    if q.data == "wallet":
        bal = get_balance(uid)
        q.message.reply_text(f"💰 Balance: ₹{bal}")
        return

    if q.data == "ref":
        link = f"https://t.me/{context.bot.username}?start=REF_{uid}"
        q.message.reply_text(f"📣 Your Link:\n{link}")
        return

    if q.data == "withdraw":
        bal = get_balance(uid)
        if bal < 100:
            q.message.reply_text("❌ Minimum ₹100")
            return

        q.message.reply_text("💳 Send UPI ID:")
        context.user_data["wait_upi"] = True
        return

    # admin approve/reject
    if q.data.startswith("approve_"):
        wid = q.data.replace("approve_", "")
        approve_withdraw(wid)
        q.message.reply_text("✔️ Approved")
        return

    if q.data.startswith("reject_"):
        wid = q.data.replace("reject_", "")
        reject_withdraw(wid)
        q.message.reply_text("❌ Rejected")
        return


def msg(update, context):
    uid = update.effective_chat.id

    if context.user_data.get("wait_upi"):
        upi = update.message.text
        amt = get_balance(uid)

        create_withdraw(uid, amt, upi)

        for admin in ADMIN_IDS:
            context.bot.send_message(
                admin,
                f"🔔 Withdraw Request\nUser: {uid}\nAmount: ₹{amt}\nUPI: {upi}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Approve", callback_data=f"approve_{uid}"),
                     InlineKeyboardButton("Reject", callback_data=f"reject_{uid}")]
                ])
            )

        update.message.reply_text("⌛ Waiting for approval...")
        context.user_data["wait_upi"] = False


# ================= SETUP ====================

def setup():
    up = Updater(TOKEN, use_context=True)
    dp = up.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(callback))
    dp.add_handler(MessageHandler(Filters.text, msg, pass_user_data=True))
    return up

dispatcher = setup()


@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, dispatcher.bot)
    dispatcher.process_update(update)
    return "ok"


@app.route("/")
def home():
    return "Bot Running!"


if __name__ == "__main__":
    app.run(port=5000)
