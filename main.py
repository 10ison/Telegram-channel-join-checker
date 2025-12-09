import sys, types, asyncio
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, ContextTypes
)

# --- FIX FOR PYTHON 3.13 ---
fake_imghdr = types.ModuleType("imghdr")
sys.modules["imghdr"] = fake_imghdr

# ---- CONFIG ----
BOT_TOKEN = "YOUR_BOT_TOKEN"
ADMIN_CHAT_ID = 8583137173
MIN_WITHDRAW = 100

CHANNELS = [
    "https://t.me/JMB_CODER",
    "https://t.me/otp_z0ne",
    "https://t.me/Alexx_network",
    "https://t.me/foxsmsshop",
    "https://t.me/vtkqo"
]
YOUTUBE_LINK = "https://youtube.com/@bizzle.editor"


# ---- DB ----
from db import init_db, add_user, set_referrer, add_referral, complete_referral, get_balance

init_db()

# ---- FLASK ----
app = Flask(__name__)


@app.route("/")
def home():
    return "BOT RUNNING!"


# ---- BOT ACTIONS ----

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    args = context.args

    add_user(uid)

    # Referral
    if args:
        ref = int(args[0])
        if ref != uid:
            set_referrer(uid, ref)
            add_referral(ref, uid)

    # animation
    await context.bot.send_chat_action(chat_id=uid, action="typing")
    await asyncio.sleep(0.5)

    btns = [
        [InlineKeyboardButton("📢 Join Channels", callback_data="join")],
        [InlineKeyboardButton("🎬 Subscribe YouTube", url=YOUTUBE_LINK)],
        [InlineKeyboardButton("✔️ Verify", callback_data="verify")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance")],
        [InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("👥 Referral Link", callback_data="ref")]
    ]

    await update.message.reply_text("🔥 Welcome!", reply_markup=InlineKeyboardMarkup(btns))


async def join(update, context):
    msg = update.callback_query.message
    text = "👇 Join all channels:\n\n"
    for c in CHANNELS:
        text += f"🚀 {c}\n"
    await msg.edit_text(text)


async def verify(update, context):
    uid = update.callback_query.from_user.id
    msg = update.callback_query.message

    for t in ["Verifying 🔍", "Verifying 🔎", "Verified 🎉"]:
        await asyncio.sleep(0.5)
        await msg.edit_text(t)

    complete_referral(uid)

    await msg.edit_text("🎉 Verified & Referral Credited!")


async def balance(update, context):
    uid = update.callback_query.from_user.id
    bal = get_balance(uid)

    await update.callback_query.message.edit_text(f"💰 Your balance: ₹{bal}")


async def withdraw(update, context):
    uid = update.callback_query.from_user.id
    bal = get_balance(uid)

    if bal < MIN_WITHDRAW:
        await update.callback_query.message.edit_text("❌ Minimum withdraw ₹100")
        return

    # send admin notification
    await context.bot.send_message(
        ADMIN_CHAT_ID,
        f"⚠️ Withdraw Request!\nUser: {uid}\nAmount: ₹{bal}"
    )

    await update.callback_query.message.edit_text("⌛ Waiting for approval…")


async def ref(update, context):
    uid = update.callback_query.from_user.id
    link = f"https://t.me/{context.bot.username}?start={uid}"
    await update.callback_query.message.edit_text(f"🔗 Your Link:\n{link}")


# ---- REGISTER HANDLERS ----

async def run_bot():
    bot = ApplicationBuilder().token(BOT_TOKEN).build()

    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(CallbackQueryHandler(join, pattern="join"))
    bot.add_handler(CallbackQueryHandler(verify, pattern="verify"))
    bot.add_handler(CallbackQueryHandler(balance, pattern="balance"))
    bot.add_handler(CallbackQueryHandler(withdraw, pattern="withdraw"))
    bot.add_handler(CallbackQueryHandler(ref, pattern="ref"))

    print("BOT STARTED 🚀")

    await bot.start()
    await bot.updater.start_polling()
    await bot.updater.idle()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    app.run(host="0.0.0.0", port=10000)
