# Какие действия сможет совершать пользователь в этом боте:
#
# просматривать блюда в меню;
# добавлять блюда в корзину по несколько раз;
# удалять блюда из корзины;
# просматривать свои блюда в корзине и их финальную стоимость с доставкой;
# заполнять и изменять свои данные: имя, телефон;
# указывать адрес через интеграцию с картами;
# оставлять комментарий к заказу.
# Оплата заказа в этом учебном боте не предусмотрена.


import telebot
from telebot import types
import json

user_info = {}



TOKEN = "7269694977:AAEHEemEKbBpp2w6N8hTZsLNCpnoqZ9_ywE"

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, 'Это бот по заказу пиццы', reply_markup=bot_start_menu())

    bot.register_next_step_handler_by_chat_id(message.chat.id, handler_start_menu)

@bot.message_handler(commands=['add_info'])
def add_info_handler(message):
    bot.send_message(message.chat.id, 'Введите ваше имя')
    bot.register_next_step_handler_by_chat_id(message.chat.id, handle_name)


def handle_name(message):
    user_info['id'] = str(message.chat.id)
    name = message.text
    user_info['name'] = name
    bot.send_message(message.chat.id, 'Введите ваш номер телефона')
    bot.register_next_step_handler_by_chat_id(message.chat.id, handle_telephone, name)


def handle_telephone(message, name):
    telephone = message.text
    user_info['phone'] = telephone
    save_info(user_info)
    bot.send_message(message.chat.id, 'Данные успешно добавлены')

def save_info(info):
    with open('data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        data['clients'].append(info)
        with open('data.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False)

def handler_start_menu(message):
    if message.text == 'Меню🍕':
        show_menu(message)
    elif message.text == 'Корзина🧺':
        show_cart(message)
    else:
        bot.send_message(message.chat.id, 'Выберите кнопку', reply_markup=bot_start_menu())


def show_menu(message):
    bot.send_message(message.chat.id, 'Меню', reply_markup=create_menu())


def bot_start_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton('Меню🍕')
    btn2 = types.KeyboardButton('Корзина🧺')
    markup.add(btn1, btn2)
    return markup

def create_menu():
    markup = types.InlineKeyboardMarkup()
    with open('products.json', 'r', encoding='utf-8') as file:
        products_list = json.load(file)
        for product in products_list['menu_items']:
            callback_data = f'item:{product["name"]}'
            button = types.InlineKeyboardButton(text=product['name'], callback_data=callback_data)
            markup.add(button)
    return markup


@bot.callback_query_handler(func=lambda call: True)
def handle_menu(call):
    if call.data.startswith('item:'):
        chosen_product = call.data.split(':')[1]

        with open('products.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            for product in data['menu_items']:
                if product['name'] == chosen_product:
                    photo = open(f'./images/{product["photo"]}', 'rb')
                    bot.send_photo(call.message.chat.id, photo, caption=f'{chosen_product}, \n {product["price"]} ')


def show_cart(message):
    ...


if __name__ == "__main__":
    bot.polling(none_stop=True)
