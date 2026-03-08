import telebot

# Put your token inside quotes
TOKEN = "8730805668:AAGnUrxv2NGZ0X1tcBoPVOLeTHzOq2PT-mQ"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🚀 Bot is running!")

bot.infinity_polling()
