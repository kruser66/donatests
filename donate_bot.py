import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from environs import Env
from textwrap import dedent


env = Env()
env.read_env()

API_TOKEN = env.str('TOKEN')
PROVIDER_TOKEN = env.str('YOOKASSA_TOKEN')

DONATE_SUMMA = {
        'RUB': [100, 200, 500, 1000],
        'USD': [1, 2, 5, 10, 20]
    }
CURRENCY = {
    'RUB': 'руб.',
    'USD': 'USD',
}
RUB_USD = 85

bot = telebot.TeleBot(API_TOKEN)


def keyboard(currency, row_width=2):
    """Генерация основного меню"""
    donate_currency, donate_value = CURRENCY[currency], DONATE_SUMMA[currency]
    start = end = 0
    markup = InlineKeyboardMarkup()

    while end < len(donate_value):
        start, end = end, min(end + row_width, len(donate_value))
        row = [
            InlineKeyboardButton(
                f'{summa} {donate_currency}',
                callback_data=f'summa_{summa}_{currency}'
                ) for summa in donate_value[start:min(end, len(donate_value))]
            ]
        markup.add(*row)
    markup.add(InlineKeyboardButton('Сменить валюту', callback_data=f'change_currency_{currency}'))
    markup.add(InlineKeyboardButton('Закрыть', callback_data='close'))
    
    return markup
    
    
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    """Привественное сообщение о функционале бота"""
    markup = telebot.types.ReplyKeyboardRemove()
    bot.send_message(
        chat_id=message.chat.id,
        text=dedent(
            f"""
            Hi {message.chat.first_name}, I am donatestBot.
            I am here to take all of your money!
            """
        ),
        reply_markup=markup
    )


@bot.message_handler(commands=['donate'])
def donate(message):
    """Основное меню для работы с /donate"""
    bot.send_photo(
        chat_id=message.chat.id,
        photo=open('support_us.jpg', 'rb'), 
        caption=dedent(
            """
            Коллеги!
            Готовы скинуться на ДР?
            """
        ),
        reply_markup=keyboard('RUB')
    )


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):

    if call.data == 'close':
        bot.delete_message(
            chat_id=call.from_user.id,
            message_id=call.message.message_id
        )
        
    elif call.data.startswith('change_currency_'):
        current_currency = call.data.split('_')[-1]
        currency = 'USD' if current_currency == 'RUB' else 'RUB'
        bot.edit_message_reply_markup(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=keyboard(currency)
        )
        
    elif call.data.startswith('summa_'):
        _, summa, currency = call.data.split('_')
        if currency == 'USD':
            summa = int(summa) * RUB_USD
        prices = [LabeledPrice(label='Donate for Friends', amount=int(summa)*100)]

        bot.send_invoice(
            chat_id=call.message.chat.id,
            title='Donate for Friends',
            description='Donate for Friends',
            invoice_payload='Donate for Friends',
            provider_token=PROVIDER_TOKEN,
            currency='RUB',
            prices=prices,
            is_flexible=False,
            start_parameter='donate-bot',
        )


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(
        pre_checkout_query.id,
        ok=True,
        error_message="Что-то пошло не так. Попробуй еще раз или попозже"
    )


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    if message.successful_payment.total_amount < 50000:
        thanks = 'Спасибо!'
    else:
        thanks = 'Вауу! Большое спасибо!'
        
    bot.send_message(
        chat_id=message.chat.id,
        text=dedent(
            f"""
                {thanks}
                
                Используй /donate если хочешь еще один платеж совершить.
            """
        ),
        parse_mode='Markdown'
    )


bot.infinity_polling()
