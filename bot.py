import telebot
from telebot import types
import random

# ================= CONFIG =================
TOKEN = "8730805668:AAGnUrxv2NGZ0X1tcBoPVOLeTHzOq2PT-mQ"  # Your bot token
bot = telebot.TeleBot(TOKEN)

# Admin IDs
ADMINS = [123456789]  # Replace with your Telegram ID

# Users storage: chat_id -> {"points": int, "referrals": int}
users = {}

# Single Netflix URL
NETFLIX_URL = "https://netflix.com/login/yourlink"  # Replace with your Netflix URL

# Channels to join (private invite links)
CHANNELS = {
    "Main": "https://t.me/+PUNNwvX-zRsyMWQ9",
    "Channel": "https://t.me/+WjxC9uqbrgVmMjk1",
    "NETFLIX DROP": "https://t.me/+0aaSyeuDsDJjNzNl"
}

# Random friendly emoji set
EMOJIS = ["❣️", "✨", "🔥", "💰", "✅", "👥", "🎬", "❤️"]
def kind_emoji():
    return random.choice(EMOJIS)

# ================= START COMMAND =================
@bot.message_handler(commands=['start'])
def start(msg):
    chat_id = msg.chat.id

    # Initialize user account
    if chat_id not in users:
        users[chat_id] = {"points": 0, "referrals": 0}

    # Referral check
    parts = msg.text.split()
    if len(parts) > 1:
        try:
            referrer_id = int(parts[1])
            if referrer_id != chat_id:
                users.setdefault(referrer_id, {"points": 0, "referrals": 0})
                users[referrer_id]["points"] += 1
                users[referrer_id]["referrals"] += 1
        except:
            pass

    # Welcome message
    bot.send_message(chat_id, f"👋 Welcome to the Netflix Redeem Bot {kind_emoji()}\n\n"
                              f"{kind_emoji()} To unlock the bot, please join the following channels first:")

    # Channel join buttons
    keyboard = types.InlineKeyboardMarkup()
    for name, link in CHANNELS.items():
        keyboard.add(types.InlineKeyboardButton(name, url=link))
    keyboard.add(types.InlineKeyboardButton(f"✅ I joined all channels {kind_emoji()}", callback_data="check_join"))
    bot.send_message(chat_id, "Join all channels then tap below:", reply_markup=keyboard)

# ================= CALLBACK HANDLER =================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id

    # Since channels are private, we just trust user confirmation
    if call.data == "check_join":
        bot.send_message(chat_id, f"✅ Channels confirmed joined! Bot unlocked {kind_emoji()}")
        send_main_menu(chat_id)

    elif call.data == "points":
        pts = users.get(chat_id, {}).get('points', 0)
        bot.send_message(chat_id, f"💰 Your Points: {pts} {kind_emoji()}\n3 points = 1 Netflix ❣️")

    elif call.data == "redeem_netflix":
        if users.get(chat_id, {}).get("points",0) >= 3:
            users[chat_id]["points"] -= 3
            bot.send_message(chat_id, f"✅ Redeemed successfully {kind_emoji()}\nHere is your Netflix URL:\n{NETFLIX_URL}")
        else:
            bot.send_message(chat_id, f"❌ Not enough points {kind_emoji()}\nYou need 3 points to redeem Netflix ❣️")

    elif call.data == "referral":
        referral_link = f"https://t.me/YourBotUsername?start={chat_id}"  # Replace with your bot username
        bot.send_message(chat_id, f"🎯 Your referral link:\n{referral_link}\nShare it with friends to earn points {kind_emoji()}")

# ================= MAIN MENU =================
def send_main_menu(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(f"💰 My Points {kind_emoji()}", callback_data="points"))
    keyboard.add(types.InlineKeyboardButton(f"🎬 Redeem Netflix {kind_emoji()}", callback_data="redeem_netflix"))
    keyboard.add(types.InlineKeyboardButton(f"👥 Earn Points / Referral {kind_emoji()}", callback_data="referral"))
    bot.send_message(chat_id, "Select an option:", reply_markup=keyboard)

# ================= ADMIN COMMAND =================
@bot.message_handler(commands=['addpoints'])
def addpoints(msg):
    if msg.chat.id not in ADMINS:
        return
    try:
        parts = msg.text.split()
        user_id = int(parts[1])
        points = int(parts[2])
        users.setdefault(user_id, {"points": 0, "referrals": 0})
        users[user_id]["points"] += points
        bot.send_message(msg.chat.id, f"✅ Added {points} points to {user_id} {kind_emoji()}")
    except:
        bot.send_message(msg.chat.id, f"Usage: /addpoints <user_id> <points> {kind_emoji()}")

# ================= RUN BOT =================
bot.infinity_polling()
