import telebot
import telebot.types as types
# from ggl import new_workbook
from help_module import process_message
from config import BOT_API
import json
from ggl_sheets import add_new_worksheets


bot = telebot.TeleBot(BOT_API)
JSON_BD = 'managers.json'

@bot.message_handler(commands=['start'])
def main(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True,
                                         one_time_keyboard=True)
    btn1 = types.KeyboardButton(text="Добавить Категорию")
    btn2 = types.KeyboardButton(text="Добавить SKU")
    btn3 = types.KeyboardButton(text="Удалить SKU")
    btn4 = types.KeyboardButton(text="Изменить Категорию у SKU")
    keyboard.row(btn1, btn2)
    keyboard.row(btn3, btn4)

    bot.send_message(message.chat.id, "Выберите действие", reply_markup=keyboard)
    bot.register_next_step_handler(callback=callback_check, message=message)

def callback_check(message: types.Message):
    if message.text == "Добавить Категорию":
        bot.send_message(message.chat.id,
                         "Выбрано: Добавить Категорию. "
                         "По-очередно вводите данные в следующем формате:\n"
                         "Название категории\nАртикул поставщика - Артикул ВБ - Опознавательное имя\n"
                         "Сохраняйте знаки-разделители '-' и пробелы между ними."
                         "В случае некорректности данных программа не "
                         "будет работать правильно. Удостоверьтесь, что артикулы верные")
        bot.register_next_step_handler(callback=add_manager, message=message)

    elif message.text == "Добавить SKU":
        bot.send_message(message.chat.id,
                         "Выбрано: Добавить SKU. "
                         "В одном сообщении на разных строках введите данные в следующем формате:\n"
                            "Артикул внутренний - Артикул ВБ - Опознавательное имя артикула\n"
                         "Сохраняйте знаки-разделители '-' и пробелы между ними."
                         "В случае некорректности данных программа не "
                         "будет работать правильно. Удостоверьтесь, что артикулы верны")
        bot.register_next_step_handler(callback=add_sku, message=message)

    elif message.text == "Удалить SKU":
        bot.send_message(message.chat.id,
                         "Выбрано: Удалить SKU. "
                         "В одном сообщении на разных строках введите данные в следующем формате:\n"
                         "Артикул ВБ\n"
                         "В случае некорректности данных программа не "
                         "будет работать правильно. Удостоверьтесь, что артикулы верны")
        bot.register_next_step_handler(callback=delete_sku, message=message)

    elif message.text == "Изменить Категорию у SKU":
        bot.send_message(message.chat.id,
                         "Выбрано: Изменить Категорию у SKU. "
                         "В одном сообщении на разных строках введите данные в следующем формате:\n"
                         "Имя старой категории\nИмя новой категории\nАртикул поставщика\n"
                         "Сохраняйте знаки-разделители '-' и пробелы между ними."
                         "В случае некорректности данных программа не "
                         "будет работать правильно. Удостоверьтесь, что артикулы верны")
        bot.register_next_step_handler(callback=change_manager, message=message)

    else:
        bot.send_message(message.chat.id, 'Простите, я вас не понимаю!')
        bot.register_next_step_handler(callback=main, message=message)
        return ''


def add_sku(message: types.Message):
    # Adding SKU's to JSON-format DB
    # Обработка переданных данных
    manager, sku_data = process_message(message, JSON_BD, 0)
    print(sku_data)
    add_new_worksheets(sku_data, manager)

    bot.send_message(message.chat.id, text='Артикулы добавлены')

def add_manager(message: types.Message):
    # Adding new manager with some SKU
    # Обработка переданных данных
    manager, sku_data = process_message(message, JSON_BD, 1)
    add_new_worksheets(sku_data, manager)

    # Создание новой рабочей книги в Google диске
    # new_workbook(manager)


    bot.send_message(message.chat.id, text='Категория добавлена')


def delete_sku(message: types.Message):
    # Deleting SKU's from JSON-format DB
    sku_data = process_message(message, JSON_BD, 2)

    bot.send_message(message.chat.id, text='Артикулы удалены')

def change_manager(message: types.Message):
    # Sending SKU's from one manager to another
    data = message.text
    manager = data.split('\n')[0]
    new_manager = data.split('\n')[1]
    print(manager)

    sku_data = [i.split(' - ') for i in data.split('\n')[2:]]
    print(sku_data)
    # Передача обработанных данных в JSON-БД
    with open(JSON_BD, mode='r', encoding='utf-8') as JSON_DB:
        data = json.load(JSON_DB)
        for sku in [sku[0] for sku in sku_data]:
            if sku in data[manager].keys():
                change_data = data[manager][sku]
                del data[manager][sku]
                data[new_manager][sku] = change_data
    with open(JSON_BD, mode='w', encoding='utf-8') as JSON_DB:
        json.dump(data, JSON_DB)

    sku_processed_data = [list(map(int, i[1:3])) for i in sku_data]
    sku_data = sku_data[:1] + sku_processed_data + sku_data[3:]


    # SENDING ONE DATA_SHEET TO ANOTHER MANAGER'S WORKBOOK

    bot.send_message(message.chat.id, text='Категория изменена')


if __name__ == "__main__":
    bot.polling(none_stop=True)

