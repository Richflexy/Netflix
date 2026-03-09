import telebot
from telebot import types
import random

# ================= CONFIG =================
TOKEN = "7463829102:AAHhD93jd93Jd93jd93jD9d3jd"
OWNER_ID = 8260250818
bot = telebot.TeleBot(TOKEN)

ADMINS = [OWNER_ID]

# proof channel ID
PROOF_CHANNEL = -1001234567890

users = {}
netflix_urls = []
redeemed_urls = {}
pending_proof = {}

CHANNELS = {
    "Main": "https://t.me/+PUNNwvX-zRsyMWQ9",
    "Channel": "https://t.me/+WjxC9uqbrgVmMjk1",
    "NETFLIX DROP": "https://t.me/+0aaSyeuDsDJjNzNl"
}

EMOJIS = ["❣️","✨","🔥","💰","✅","👥","🎬","❤️"]
def kind_emoji():
    return random.choice(EMOJIS)

# ================= JOIN CHECK =================
def check_join(user_id):
    try:
        for link in CHANNELS.values():
            username = link.replace("https://t.me/","")
            member = bot.get_chat_member(username, user_id)

            if member.status not in ["member","administrator","creator"]:
                return False

        return True
    except:
        return False

# ================= START =================
@bot.message_handler(commands=['start'])
def start(msg):

    chat_id = msg.chat.id

    if chat_id not in users:
        users[chat_id] = {"points":0,"invited":0,"joined":False}

    parts = msg.text.split()

    if len(parts)>1:
        try:
            referrer=int(parts[1])
            if referrer!=chat_id:
                users[chat_id]["referrer"]=referrer
        except:
            pass

    send_join_menu(chat_id)

# ================= JOIN MENU =================
def send_join_menu(chat_id):

    keyboard = types.InlineKeyboardMarkup()

    for name,link in CHANNELS.items():
        keyboard.add(types.InlineKeyboardButton(name,url=link))

    keyboard.add(types.InlineKeyboardButton(
        f"✅ I Joined All Channels {kind_emoji()}",
        callback_data="check_join"
    ))

    bot.send_message(
        chat_id,
        f"👋 Welcome {kind_emoji()}\n\nJoin all channels to unlock bot:",
        reply_markup=keyboard
    )

# ================= CALLBACK =================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    chat_id = call.message.chat.id

    if call.data=="check_join":

        if not check_join(chat_id):
            bot.answer_callback_query(
                call.id,
                "❌ You didn't join all channels!",
                show_alert=True
            )
            return

        users[chat_id]["joined"]=True

        referrer = users.get(chat_id,{}).get("referrer")

        if referrer and referrer in users:
            users[referrer]["points"]+=1
            users[referrer]["invited"]+=1
            del users[chat_id]["referrer"]

        bot.send_message(chat_id,f"✅ Channels verified! Bot unlocked {kind_emoji()}")
        send_main_menu(chat_id)

    elif call.data=="points":

        pts = users.get(chat_id,{}).get("points",0)

        if chat_id==OWNER_ID:
            pts="Unlimited 🔥"

        bot.send_message(
            chat_id,
            f"💰 Your Points: {pts}\n3 points = 1 Netflix {kind_emoji()}"
        )

    elif call.data=="redeem_netflix":

        if pending_proof.get(chat_id):
            bot.send_message(chat_id,"📸 Send previous screenshot proof first.")
            return

        if not netflix_urls:
            bot.send_message(chat_id,f"❌ No Netflix URLs left {kind_emoji()}")
            return

        if chat_id==OWNER_ID:
            account=random.choice(netflix_urls)

            bot.send_message(chat_id,f"""✅ Order Completed

{account}

Send screenshot proof here.""")
            pending_proof[chat_id]=True
            return

        if users.get(chat_id,{}).get("points",0)>=3:

            if chat_id not in redeemed_urls:
                redeemed_urls[chat_id]=[]

            available=[u for u in netflix_urls if u not in redeemed_urls[chat_id]]

            if not available:
                bot.send_message(chat_id,"❌ No new Netflix URLs left")
                return

            account=random.choice(available)

            redeemed_urls[chat_id].append(account)
            users[chat_id]["points"]-=3
            pending_proof[chat_id]=True

            bot.send_message(chat_id,f"""✅ Order Successfully Completed

{account}

📸 Send screenshot proof here to unlock bot again.""")

        else:
            bot.send_message(chat_id,"❌ Not enough points")

    elif call.data=="referral":

        bot_username=bot.get_me().username
        link=f"https://t.me/{bot_username}?start={chat_id}"

        invited=users.get(chat_id,{}).get("invited",0)

        bot.send_message(chat_id,f"""💰 Invite Users And Earn 1 POINT

💹 Your Link:
{link}

👥 Invited: {invited}
""")

# ================= SCREENSHOT =================
@bot.message_handler(content_types=['photo'])
def screenshot(msg):

    chat_id = msg.chat.id

    if not users.get(chat_id,{}).get("joined"):
        send_join_menu(chat_id)
        return

    if not pending_proof.get(chat_id):
        bot.send_message(chat_id,"❌ No pending proof required.")
        return

    username = msg.from_user.username
    if username is None:
        username="NoUsername"

    caption=f"""
📸 New Netflix Proof

User ID: {chat_id}
Username: @{username}
"""

    bot.send_photo(
        PROOF_CHANNEL,
        msg.photo[-1].file_id,
        caption=caption
    )

    pending_proof[chat_id]=False

    bot.send_message(
        chat_id,
        f"✅ Screenshot received {kind_emoji()}\nBot unlocked again."
    )

    send_main_menu(chat_id)

# ================= MAIN MENU =================
def send_main_menu(chat_id):

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(types.InlineKeyboardButton(
        f"💰 My Points {kind_emoji()}",
        callback_data="points"
    ))

    keyboard.add(types.InlineKeyboardButton(
        f"🎬 Redeem Netflix {kind_emoji()}",
        callback_data="redeem_netflix"
    ))

    keyboard.add(types.InlineKeyboardButton(
        f"👥 Earn Points / Referral {kind_emoji()}",
        callback_data="referral"
    ))

    bot.send_message(chat_id,"Select option:",reply_markup=keyboard)

# ================= ADMIN COMMANDS =================

@bot.message_handler(commands=['stats'])
def stats(msg):

    if msg.chat.id not in ADMINS:
        return

    total_points=sum(u["points"] for u in users.values())

    bot.send_message(
        msg.chat.id,
        f"""
📊 BOT STATS

Users: {len(users)}
Total Points: {total_points}
Netflix URLs: {len(netflix_urls)}
"""
    )

# ================= ADD POINTS =================
@bot.message_handler(commands=['addpoints'])
def addpoints(msg):

    if msg.chat.id not in ADMINS:
        return

    try:
        parts=msg.text.split()

        user_id=int(parts[1])
        points=int(parts[2])

        users.setdefault(user_id,{"points":0,"invited":0,"joined":True})

        users[user_id]["points"]+=points

        bot.send_message(msg.chat.id,f"✅ Added {points} points")

    except:
        bot.send_message(msg.chat.id,"Usage:\n/addpoints user_id points")

# ================= ADD NETFLIX =================
@bot.message_handler(commands=['addnetflix'])
def add_netflix(msg):

    if msg.chat.id not in ADMINS:
        return

    try:

        urls=msg.text.split("\n")[1:]

        netflix_urls.clear()

        for u in urls:
            u=u.strip()
            if u:
                netflix_urls.append(u)

        redeemed_urls.clear()

        bot.send_message(msg.chat.id,f"✅ Added {len(netflix_urls)} Netflix URLs")

    except Exception as e:
        bot.send_message(msg.chat.id,f"Error: {e}")

# ================= RUN =================
print("Bot running...")
bot.infinity_polling()
