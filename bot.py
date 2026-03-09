import telebot
from telebot import types
import json

BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"

bot = telebot.TeleBot(BOT_TOKEN)

CHANNELS = [
"@channel1",
"@channel2"
]

PROOF_CHANNEL = -1003811293838

ADMINS = [123456789]

USERS_FILE = "users.json"

users = {}

# ---------------- LOAD USERS ----------------

def load_users():
    global users
    try:
        with open(USERS_FILE,"r") as f:
            users = json.load(f)
    except:
        users = {}

def save_users():
    with open(USERS_FILE,"w") as f:
        json.dump(users,f)

load_users()

# ---------------- JOIN CHECK ----------------

def check_join(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel,user_id)
            if member.status not in ["member","administrator","creator"]:
                return False
        except:
            return False
    return True

# ---------------- START ----------------

@bot.message_handler(commands=['start'])
def start(msg):

    user_id = str(msg.chat.id)

    if user_id not in users:
        users[user_id] = {
            "points":0,
            "invited":0,
            "redeemed":False
        }
        save_users()

    if not check_join(msg.chat.id):

        markup = types.InlineKeyboardMarkup()

        for ch in CHANNELS:
            markup.add(types.InlineKeyboardButton(
                "Join Channel",
                url=f"https://t.me/{ch.replace('@','')}"
            ))

        markup.add(types.InlineKeyboardButton(
            "✅ I Joined",
            callback_data="check_join"
        ))

        bot.send_message(
            msg.chat.id,
            "⚠️ Join all channels first to use the bot.",
            reply_markup=markup
        )
        return

    bot.send_message(
        msg.chat.id,
        "✅ Bot unlocked!\n\nSend screenshot proof."
    )

# ---------------- RECHECK BUTTON ----------------

@bot.callback_query_handler(func=lambda call: call.data=="check_join")
def recheck(call):

    user_id = call.message.chat.id

    if check_join(user_id):

        bot.answer_callback_query(call.id,"Verified ✅")

        bot.send_message(
            user_id,
            "🎉 Verification complete!\n\nSend screenshot proof."
        )

    else:

        bot.answer_callback_query(
            call.id,
            "❌ You didn't join all channels",
            show_alert=True
        )

# ---------------- SCREENSHOT HANDLER ----------------

@bot.message_handler(content_types=['photo'])
def screenshot(msg):

    user_id = str(msg.chat.id)

    caption = f"""
📸 New Proof Screenshot

👤 User ID: {user_id}
👤 Username: @{msg.from_user.username}

"""

    bot.forward_message(
        PROOF_CHANNEL,
        msg.chat.id,
        msg.message_id
    )

    bot.send_message(
        PROOF_CHANNEL,
        caption
    )

    bot.send_message(
        msg.chat.id,
        "✅ Screenshot received!\n\nYour proof has been submitted."
    )

# ---------------- REDEEM ----------------

@bot.message_handler(commands=['redeem'])
def redeem(msg):

    user_id = str(msg.chat.id)

    if users[user_id]["points"] < 2:

        bot.send_message(
            msg.chat.id,
            "❌ You need 2 referrals to redeem Netflix."
        )
        return

    if users[user_id]["redeemed"]:

        bot.send_message(
            msg.chat.id,
            "⚠️ You already redeemed."
        )
        return

    users[user_id]["redeemed"] = True
    save_users()

    bot.send_message(
        msg.chat.id,
        "🎉 Congratulations!\n\nHere is your Netflix account:\n\nhttps://example.com"
    )

# ---------------- STATS ----------------

@bot.message_handler(commands=['stats'])
def stats(msg):

    if msg.chat.id not in ADMINS:
        return

    total_users = len(users)
    total_points = sum(u["points"] for u in users.values())

    bot.send_message(
        msg.chat.id,
        f"""
📊 BOT STATS

👥 Users: {total_users}
⭐ Points Given: {total_points}
"""
    )

# ---------------- RUN ----------------

print("Bot running...")

bot.infinity_polling()
