import telebot
from telebot import types
import random

# ================= CONFIG =================
TOKEN = "8730805668:AAGnUrxv2NGZ0X1tcBoPVOLeTHzOq2PT-mQ"
OWNER_ID = 8260250818
bot = telebot.TeleBot(TOKEN)

ADMINS = [OWNER_ID]

users = {}  # chat_id -> {"points": int, "invited": int, "joined": bool}
netflix_urls = []  # Netflix URLs queue
redeemed_urls = {}  # track urls per user to avoid repetition

CHANNELS = {
    "Main": "https://t.me/+PUNNwvX-zRsyMWQ9",
    "Channel": "https://t.me/+WjxC9uqbrgVmMjk1",
    "NETFLIX DROP": "https://t.me/+0aaSyeuDsDJjNzNl"
}

EMOJIS = ["❣️", "✨", "🔥", "💰", "✅", "👥", "🎬", "❤️"]
def kind_emoji(): return random.choice(EMOJIS)

# ================= START =================
@bot.message_handler(commands=['start'])
def start(msg):
    chat_id = msg.chat.id
    if chat_id not in users:
        users[chat_id] = {"points": 0, "invited": 0, "joined": False}

    # Referral
    parts = msg.text.split()
    if len(parts) > 1:
        try:
            referrer = int(parts[1])
            if referrer != chat_id:
                users[chat_id]["referrer"] = referrer
        except: pass

    # Ask to join channels first
    bot.send_message(chat_id, f"👋 Welcome! {kind_emoji()}\nJoin all channels to unlock the bot:")
    keyboard = types.InlineKeyboardMarkup()
    for name, link in CHANNELS.items():
        keyboard.add(types.InlineKeyboardButton(name, url=link))
    keyboard.add(types.InlineKeyboardButton(f"✅ I joined all channels {kind_emoji()}", callback_data="check_join"))
    bot.send_message(chat_id, "Join channels then tap below:", reply_markup=keyboard)

# ================= CALLBACK =================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id

    if call.data=="check_join":
        users[chat_id]["joined"] = True

        # Give referral point if exists
        referrer = users.get(chat_id, {}).get("referrer")
        if referrer and referrer in users:
            users[referrer]["points"] += 1
            users[referrer]["invited"] += 1
            del users[chat_id]["referrer"]

        bot.send_message(chat_id, f"✅ Channels joined! Bot unlocked {kind_emoji()}")
        send_main_menu(chat_id)

    elif call.data=="points":
        pts = users.get(chat_id, {}).get("points", 0)
        if chat_id == OWNER_ID:
            pts = "Unlimited 🔥"
        bot.send_message(chat_id, f"💰 Your Points: {pts} {kind_emoji()}\n3 points = 1 Netflix ❣️")

    elif call.data=="redeem_netflix":
        if not netflix_urls:
            bot.send_message(chat_id, f"❌ No Netflix URLs left {kind_emoji()}")
            return

        if chat_id == OWNER_ID:
            account = random.choice(netflix_urls)
            bot.send_message(chat_id,
f"""✅ Order Successfully Completed..📧 Account Direct login url ❣️👇🏻
{account}

How to login? :- just tap on link you'll automatically login in Netflix in your browser ❤️

🎊Thanks For Using Our Bot🎊~Send Screenshot To @StarLuxHub ❣️""")
            return

        if users.get(chat_id, {}).get("points",0) >= 3:
            # Initialize redeemed list for user
            if chat_id not in redeemed_urls:
                redeemed_urls[chat_id] = []

            # Get available urls not yet redeemed by this user
            available = [u for u in netflix_urls if u not in redeemed_urls[chat_id]]
            if not available:
                bot.send_message(chat_id, f"❌ No new Netflix URLs left {kind_emoji()}")
                return

            account = random.choice(available)
            redeemed_urls[chat_id].append(account)  # mark as redeemed
            users[chat_id]["points"] -= 3
            bot.send_message(chat_id,
f"""✅ Order Successfully Completed..📧 Account Direct login url ❣️👇🏻
{account}

How to login? :- just tap on link you'll automatically login in Netflix in your browser ❤️

🎊Thanks For Using Our Bot🎊~Send Screenshot To @StarLuxHub ❣️""")
        else:
            bot.send_message(chat_id, f"❌ Not enough points {kind_emoji()}")

    elif call.data=="referral":
        bot_username = bot.get_me().username
        referral_link = f"https://t.me/{bot_username}?start={chat_id}"
        invited = users.get(chat_id, {}).get("invited",0)
        bot.send_message(chat_id,
f"""💰 Invite Users And Earn 1 POINT
💹 Your Link: {referral_link}
🎯 You Invited : {invited} Users {kind_emoji()}""")

# ================= MAIN MENU =================
def send_main_menu(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(f"💰 My Points {kind_emoji()}", callback_data="points"))
    keyboard.add(types.InlineKeyboardButton(f"🎬 Redeem Netflix {kind_emoji()}", callback_data="redeem_netflix"))
    keyboard.add(types.InlineKeyboardButton(f"👥 Earn Points / Referral {kind_emoji()}", callback_data="referral"))
    bot.send_message(chat_id, "Select an option:", reply_markup=keyboard)

# ================= ADMIN: ADD POINTS =================
@bot.message_handler(commands=['addpoints'])
def addpoints(msg):
    if msg.chat.id not in ADMINS: return
    try:
        parts = msg.text.split()
        user_id = int(parts[1])
        points = int(parts[2])
        users.setdefault(user_id, {"points":0,"invited":0,"joined":True})
        users[user_id]["points"] += points
        bot.send_message(msg.chat.id,f"✅ Added {points} points to {user_id} {kind_emoji()}")
    except:
        bot.send_message(msg.chat.id,f"Usage: /addpoints <user_id> <points> {kind_emoji()}")

# ================= ADMIN: REPLACE NETFLIX URLS =================
@bot.message_handler(commands=['addnetflix'])
def add_netflix(msg):
    if msg.chat.id not in ADMINS: return
    try:
        urls = msg.text.split("\n")[1:]  # each url in new line
        netflix_urls.clear()  # Clear old URLs
        for u in urls:
            u = u.strip()
            if u: netflix_urls.append(u)
        redeemed_urls.clear()  # Reset redeemed urls for all users
        bot.send_message(msg.chat.id,f"✅ Replaced Netflix URLs with {len(urls)} new ones {kind_emoji()}")
    except Exception as e:
        bot.send_message(msg.chat.id,f"❌ Error: {e}")

# ================= RUN BOT =================
bot.infinity_polling()
