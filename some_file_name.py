import telebot

API_TOKEN = '<api_token>'

bot = telebot.TeleBot(API_TOKEN)


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
Hi there, I am donatestBot.
I am here to take all of your money!\
""")


@bot.message_handler(commands=['donate'])
def donate_moar_plz(message):
    """
    Возможно, с помощью этой команды можно будет получить меню для донатов.
    А может быть и нет...
    """


bot.infinity_polling()
