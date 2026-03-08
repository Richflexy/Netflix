import telebot

TOKEN = "8730805668:AAGnUrxv2NGZ0X1tcBoPVOLeTHzOq2PT-mQ"
bot = telebot.TeleBot(TOKEN)

# Users points
users = {}

# Admin IDs
ADMINS = [123456789]  # <-- replace with your Telegram ID

# Single Netflix URL
NETFLIX_URL = "https://netflix.com/login/yourlink"

# User commands
@bot.message_handler(commands=['start'])
def start(msg):
    chat_id = msg.chat.id
    if chat_id not in users:
        users[chat_id] = 0
    bot.send_message(chat_id,
        "🔥 Welcome to the Netflix Redeem Bot!\n💰 3 Points = 1 Netflix URL"
    )
    send_main_menu(chat_id)

def send_main_menu(chat_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("💰 My Points", callback_data="points"))
    keyboard.add(telebot.types.InlineKeyboardButton("🎬 Redeem Netflix", callback_data="redeem_netflix"))
    keyboard.add(telebot.types.InlineKeyboardButton("👥 Invite Friends", callback_data="invite"))
    bot.send_message(chat_id, "Select an option:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    if call.data == "points":
        bot.send_message(chat_id, f"💰 Your Points: {users.get(chat_id,0)}")
    elif call.data == "redeem_netflix":
        if users.get(chat_id,0) >= 3:
            users[chat_id] -= 3
            bot.send_message(chat_id, f"✅ Redeemed!\nHere is your Netflix URL:\n{NETFLIX_URL}")
        else:
            bot.send_message(chat_id, "❌ Not enough points (3 points needed).")
    elif call.data == "invite":
        bot.send_message(chat_id, "👥 Invite your friends to earn points!")

# Admin command
@bot.message_handler(commands=['addpoints'])
def addpoints(msg):
    if msg.chat.id not in ADMINS:
        return
    try:
        parts = msg.text.split()
        user_id = int(parts[1])
        points = int(parts[2])
        users[user_id] = users.get(user_id,0) + points
        bot.send_message(msg.chat.id, f"✅ Added {points} points to {user_id}")
    except:
        bot.send_message(msg.chat.id, "Usage: /addpoints <user_id> <points>")

bot.infinity_polling()
