import telebot
from telebot import types
import random

# ================= CONFIG =================
TOKEN = "8730805668:AAGnUrxv2NGZ0X1tcBoPVOLeTHzOq2PT-mQ"  # Your bot token
bot = telebot.TeleBot(TOKEN)

# Admin IDs
ADMINS = [8260250818]  # Replace with your Telegram ID (owner)

# Users storage: chat_id -> {"points": int, "referrals": int}
users = {}

# Netflix URLs list (updated via /addnetflix)
netflix_urls = []

# Channels to join before using bot
CHANNELS = {
    "Main": "@YourMainChannelUsername",
    "Channel": "@YourSecondChannelUsername",
    "NETFLIX DROP": "@NetflixDropChannel"
}

# Friendly emoji set (randomized)
EMOJIS = ["❣️", "✨", "🔥", "💰", "✅", "👥", "🎬", "❤️"]
def kind_emoji():
    return random.choice(EMOJIS)

# ================= START COMMAND =================
@bot.message_handler(commands=['start'])
def start(msg):
    chat_id = msg.chat.id

    if chat_id not in users:
        users[chat_id] = {"points":0, "referrals":0}

    # Referral handling
    parts = msg.text.split()
    if len(parts) > 1:
        try:
            ref_id = int(parts[1])
            if ref_id != chat_id:
                users.setdefault(ref_id, {"points":0, "referrals":0})
                users[ref_id]["points"] += 1
                users[ref_id]["referrals"] += 1
        except:
            pass

    bot.send_message(chat_id, f"👋 Welcome! {kind_emoji()}\n"
                              f"{kind_emoji()} To unlock, join all channels first:")

    keyboard = types.InlineKeyboardMarkup()
    for name, username in CHANNELS.items():
        keyboard.add(types.InlineKeyboardButton(name, url=f"https://t.me/{username[1:]}"))
    keyboard.add(types.InlineKeyboardButton(f"✅ I joined all channels {kind_emoji()}", callback_data="check_join"))
    bot.send_message(chat_id, "Join channels then tap below:", reply_markup=keyboard)

    # Referral link
    referral_link = f"https://t.me/YourBotUsername?start={chat_id}"  # replace with your bot username
    bot.send_message(chat_id, f"🎯 Share your referral link to earn points:\n{referral_link} {kind_emoji()}")

# ================= CALLBACK HANDLER =================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id

    if call.data == "check_join":
        not_joined = []
        for name, username in CHANNELS.items():
            try:
                member = bot.get_chat_member(username, chat_id)
                if member.status in ["left","kicked"]:
                    not_joined.append(name)
            except:
                not_joined.append(name)

        if not_joined:
            bot.send_message(chat_id, f"❌ You must join: {', '.join(not_joined)} {kind_emoji()}")
        else:
            bot.send_message(chat_id, f"✅ All channels joined! Bot unlocked {kind_emoji()}")
            send_main_menu(chat_id)

    elif call.data == "points":
        pts = users.get(chat_id, {}).get("points",0)
        bot.send_message(chat_id, f"💰 Your Points: {pts} {kind_emoji()}")

    elif call.data == "redeem_netflix":
        if users.get(chat_id, {}).get("points",0) >= 3:
            if not netflix_urls:
                bot.send_message(chat_id, f"❌ No Netflix URLs available yet {kind_emoji()}")
                return
            users[chat_id]["points"] -= 3
            # Give first URL in list and rotate it
            url = netflix_urls.pop(0)
            netflix_urls.append(url)
            bot.send_message(chat_id, f"✅ Redeemed 3 points {kind_emoji()}\nHere is your Netflix URL:\n{url}")
        else:
            bot.send_message(chat_id, f"❌ Not enough points {kind_emoji()}\nYou need 3 points to redeem ❣️")

# ================= MAIN MENU =================
def send_main_menu(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(f"💰 My Points {kind_emoji()}", callback_data="points"))
    keyboard.add(types.InlineKeyboardButton(f"🎬 Redeem Netflix {kind_emoji()}", callback_data="redeem_netflix"))
    bot.send_message(chat_id, "Select an option:", reply_markup=keyboard)

# ================= ADMIN COMMAND =================
@bot.message_handler(commands=['addpoints'])
def addpoints(msg):
    if msg.chat.id not in ADMINS:
        return
    try:
        parts = msg.text.split()
        user_id = int(parts[1])
        pts = int(parts[2])
        users.setdefault(user_id, {"points":0,"referrals":0})
        users[user_id]["points"] += pts
        bot.send_message(msg.chat.id, f"✅ Added {pts} points to {user_id} {kind_emoji()}")
    except:
        bot.send_message(msg.chat.id, f"Usage: /addpoints <user_id> <points> {kind_emoji()}")

# ================= ADMIN ADD NETFLIX URLS =================
@bot.message_handler(commands=['addnetflix'])
def addnetflix(msg):
    if msg.chat.id not in ADMINS:
        return
    global netflix_urls
    # Split by lines and ignore empty lines
    urls = [line.strip() for line in msg.text.splitlines()[1:] if line.strip()]
    if urls:
        netflix_urls = urls
        bot.send_message(msg.chat.id, f"✅ Updated Netflix URLs: {len(urls)} {kind_emoji()}")
    else:
        bot.send_message(msg.chat.id, f"❌ No URLs found! Make sure each URL is on a separate line {kind_emoji()}")

# ================= RUN BOT =================
bot.infinity_polling()
