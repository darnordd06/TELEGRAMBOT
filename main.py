import sqlite3
import requests
import telebot

bot = telebot.TeleBot('2119118487:AAFvr-PCSNt2Brv3o6iVG-TYIWrbF1TbbyQ')

otvet = telebot.types.InlineKeyboardMarkup(row_width=1)
new_button1 = telebot.types.InlineKeyboardButton("✅ Принять правила проекта", callback_data='good')
otvet.add(new_button1)

mm = telebot.types.ReplyKeyboardMarkup(True)
button1 = telebot.types.KeyboardButton('Играть')
button2 = telebot.types.KeyboardButton('Тех. поддержка')
button3 = telebot.types.KeyboardButton('Личный кабинет')
mm.row(button1)
mm.row(button2, button3)

game_count = 0
win_count = 0
lose_count = 0
withdraw_count = 0
deposit_count = 0


@bot.message_handler(commands=['start'])
def send_welcome(message):
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS login_id(
        id INTEGER
    )""")

    connect.commit()

    # check id in fields
    people_id = message.chat.id
    cursor.execute(f"SELECT id FROM login_id WHERE id = {people_id}")
    data = cursor.fetchone()
    if data is None:
        # add values in fields
        user_id = [message.chat.id]
        cursor.execute("INSERT INTO login_id VALUES(?);", user_id)
        connect.commit()
    else:
        bot.send_message(message.chat.id, 'Такой пользователь уже существует')


@bot.message_handler(commands=['delete'])
def delete_from_db(message):
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()

    people_id = message.chat.id
    cursor.execute(f"DELETE FROM login_id WHERE id = {people_id}")
    connect.commit()
    bot.send_message(message.chat.id, 'Пользователь был удален')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == "good":
                bot.send_message(call.message.chat.id, "✅ Правила проекта приняты")
                bot.send_message(message.from_user.id,
                                 f'🙋🏻‍♀️ Добро пожаловать, <b>{message.from_user.first_name}</b> \n Мы '
                                 f'представляем Вам '
                                 f'нашу викторину на знание географии.', reply_markup=mm,
                                 parse_mode='HTML')


    except Exception as e:
        print(repr(e))


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.from_user.id, 'Привет!')
    elif message.text.lower() == 'тех. поддержка':
        bot.send_message(message.from_user.id, '💻 Техническая поддержка - @РандомныйНик')
    elif message.text.lower() == 'личный кабинет':
        bot.send_message(message.from_user.id, f'<b> 💸 Ваш личный кабинет </b> \n\n Баланс: 0.0 ₽ (0.0 ₴) \n\n'
                                               f'<b>⚠️ Базовый аккаунт </b> \n\n'
                                               f'Игр всего - {game_count} \nИгр выиграно - '
                                               f'{win_count} \n'
                                               f'Игр проиграно - {lose_count}\n\n'
                                               f'Заявок на вывод - {withdraw_count}\n'
                                               f'Пополнений - {deposit_count} \n\n'
                                               f'🧙🏻‍♂️ Ваша реферальная ссылка - ', parse_mode='HTML')
    else:
        bot.send_message(message.from_user.id, 'Не понимаю, что это значит.')


bot.polling(none_stop=True)
