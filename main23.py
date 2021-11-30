import requests
import datetime
import pymysql
import random
import time
from config import tg_bot_token, open_weather_token, host, user, password, db_name
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from datetime import datetime

want_to_delete = False
admin_start = False
bot = Bot(token=tg_bot_token)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    connect = pymysql.connect(
        host=host,
        port=3306,
        user=user,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = connect.cursor()
    # cursor.execute("""CREATE TABLE IF NOT EXISTS login_id(id INTEGER)""")
    # connect.commit()

    # check id in fields
    people_id = message.chat.id
    user_first_name = message.from_user.first_name
    user_last_name = message.from_user.last_name
    cursor.execute(f"SELECT id FROM login_id WHERE id = {people_id}")
    data = cursor.fetchone()
    if data is None:
        sqlreq = f"""INSERT INTO login_id (id, first_name, last_name) VALUES ('{people_id}', '{user_first_name}', '{user_last_name}')"""
        cursor.execute(sqlreq)
        connect.commit()
        await bot.send_message(89930973, f'Подключился новый участник {people_id}, {user_first_name} {user_last_name}')
        await bot.send_message(1878928932,
                               f'Подключился новый участник {people_id}, {user_first_name} {user_last_name}')
    # else:
    #   print(f'Пользователь {people_id} уже в базе!')
    await message.answer("🏙️ Введи название города: ")


@dp.message_handler(commands=['delete'])
async def delete_from_db(message: types.Message):
    global want_to_delete
    if message.chat.id == 89930973 or 1878928932:
        await message.answer('Введите id пользователя, которого хотите удалить: ')
        want_to_delete = True
    else:
        await message.answer('❌ У вас недостаточно прав для использования команды')
    # print(f'Пользователь {message.chat.id} пытался воспользоваться /delete')


@dp.message_handler(commands=['admin'])
async def admin_func(message: types.Message):
    global admin_start
    if message.chat.id == 89930973 or 1878928932:
        admin_start = True
        await message.answer('Введите сообщение для рассылки:')
    else:
        await message.answer('❌ У вас недостаточно прав для использования команды')


@dp.message_handler()
async def get_weather(message: types.Message):
    global want_to_delete
    global admin_start
    if admin_start:
        admin_start = False
        connect = pymysql.connect(
            host=host,
            port=3306,
            user=user,
            password=password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = connect.cursor()
        cursor.execute(f"SELECT id FROM login_id")
        data = cursor.fetchall()
        for item in data:
            await bot.send_message(item['id'], f'Тестовая рассылка всем контактам - {message.text}')
            time.sleep(0.1)
        return

    if want_to_delete and (message.chat.id == (89930973 or 1878928932)):
        connect = pymysql.connect(
            host=host,
            port=3306,
            user=user,
            password=password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = connect.cursor()
        if not message.text.isdigit():
            await message.answer('Введен некорректный id пользователя')
            return
        people_id = int(message.text)
        cursor.execute(f"SELECT id FROM login_id WHERE id = {people_id}")
        data = cursor.fetchone()
        if data != None:
            cursor.execute(f"DELETE FROM login_id WHERE id = {people_id}")
            connect.commit()
            await message.answer('Пользователь был удален')
            print('Пользователь был удален')
            want_to_delete = False
        else:
            await message.answer('Пользователя нет в базе')
    else:
        code_to_smile = {
            "Clear": "Ясно \U00002600",
            "Clouds": "Облачно \U00002601",
            "Rain": "Дождь \U00002614",
            "Drizzle": "Дождь \U00002614",
            "Thunderstorm": "Гроза \U000026A1",
            "Snow": "Снег \U0001F328",
            "Mist": "Туман \U0001F32B"
        }

        try:
            r = requests.get(
                f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={open_weather_token}&units=metric")
            data = r.json()
            city = data["name"]
            cur_weather = data["main"]["temp"]

            weather_description = data["weather"][0]["main"]
            if weather_description in code_to_smile:
                wd = code_to_smile[weather_description]
            else:
                wd = "Посмотри в окно, не пойму что там за погода!"
            humidity = data["main"]["humidity"]
            pressure = data["main"]["pressure"]
            wind = data["wind"]["speed"]
            sunrise_timestamp = datetime.fromtimestamp(data["sys"]["sunrise"])
            sunset_timestamp = datetime.fromtimestamp(data["sys"]["sunset"])
            length_of_the_day = datetime.fromtimestamp(
                data["sys"]["sunset"]) - datetime.fromtimestamp(data["sys"]["sunrise"])

            cold_list = [
                f'Сегодня только зимняя куртка, теплые штаны и варежки\n{wd} | Температура: {int(cur_weather)} C°',
                f'Сегодня можно надеть зимнюю куртку с подштанниками\n{wd} | Температура: {int(cur_weather)} C°',
                f'Сегодня надевайте теплые штаны с подштанниками и зимнюю куртку\n{wd} | Температура: {int(cur_weather)} C°']
            cold_list_random = random.randint(0, 2)

            cold_sticker = [r'CAACAgIAAxkBAAEDX7thoxP8fxjtYTG8BVtEvHgfdCf5dwAChgAD9wLIDw5AaN32E2B9IgQ',
                            r'CAACAgIAAxkBAAEDX71hoxUHqYQaSDpZ6HHbdKEv3kGXogACOgEAAvcCyA882EfADBzI3CIE',
                            r'CAACAgIAAxkBAAEDX8FhoxUzmVGboXMAARIsvaEo8G4Vjy0AAiIJAAIYQu4IsJEOZWcMR6AiBA']
            cold_sticker_random = random.randint(0, 2)

            not_so_cold = [f'Сегодня можно надеть не очень теплую куртку\n{wd} | Температура: {int(cur_weather)} C°',
                           f'Сегодня можно надеть осеннюю куртку, но с шапкой, увы\n{wd} | Температура: {int(cur_weather)} C°',
                           f'Сегодня лучше надеть куртку и шапку с шарфом\n{wd} | Температура: {int(cur_weather)} C°']
            not_so_cold_random = random.randint(0, 2)

            cold_but_not_so_cold = [
                f'Сегодня будет достаточно свитера с теплой курткой\n{wd} | Температура: {int(cur_weather)} C°',
                f'Сегодня можно надеть свитер под теплую куртку, не забудьте подштанники\n{wd} | Температура: {int(cur_weather)} C°',
                f'Сегодня можно надеть теплую куртку с подштанниками и джинсами\n{wd} | Температура: {int(cur_weather)} C°']

            cold_but_not_so_cold_random = random.randint(0, 2)

            if cur_weather < 10 and cur_weather > -5 and wind > 5 and wind < 10:  # НЕ ХОЛОДНО, НО ВЕТЕР ВЫШЕ НОРМЫ ДО 10 М/С
                await message.reply(
                    f'Сегодня можно надеть не очень теплую куртку\n{wd} | Температура: {int(cur_weather)} C°')

            elif cur_weather < -20:  # ОЧЕНЬ ХОЛОДНО
                await message.reply(cold_list[cold_list_random])
                await message.answer_sticker(cold_sticker[cold_sticker_random])

            elif cur_weather < -5 and cur_weather > -20:  # ДОСТАТОЧНО ХОЛОДНО
                await message.reply(not_so_cold[cold_but_not_so_cold_random])

            elif cur_weather < 10 and cur_weather > -5:  # НЕ ОЧЕНЬ ХОЛОДНО
                await message.reply(not_so_cold[not_so_cold_random])

            elif cur_weather > 20 and wd == 'Дождь \U00002614':
                await message.reply(
                    f'Сегодня можно надеть шорты и майку, не забывая о зонтике\n{wd} | Температура: {int(cur_weather)} C°')
            elif cur_weather > 25 and wd == 'Ясно \U00002600' and humidity < 50:
                await message.reply(f'Надевайте шорты и майку, помните о палящем солнце ☀️\n'
                                    f'Не забудьте про воду, маленькая влажность 💧\n{wd} | Температура: {int(cur_weather)} C°')
            else:
                await message.reply(f"***{datetime.now().strftime('%Y-%m-%d %H:%M')}***\n"
                                    f"Погода в городе: {city}\nТемпература: {cur_weather}C° {wd}\n"
                                    f"Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст\nВетер: {wind} м/с\n"
                                    f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\nПродолжительность дня: {length_of_the_day}"
                                    )
        except:
            await message.reply("\U00002620 Проверьте название города \U00002620")


if __name__ == '__main__':
    executor.start_polling(dp)
