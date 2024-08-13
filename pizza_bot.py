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
cart_items = []
ITEMS_PER_PAGE = 5


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
    alph = []
    try:
        telephone = int(telephone)
        user_info['phone'] = telephone
        save_info(user_info)
        bot.send_message(message.chat.id, 'Данные успешно добавлены')
    except:
        bot.send_message(message.chat.id, 'Телефон введен не правильно')
        bot.send_message(message.chat.id, 'Введите ваш номер телефона')
        bot.register_next_step_handler_by_chat_id(message.chat.id, handle_telephone, name)



def save_info(info):
    with open('data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        data['clients'].append(info)
        with open('data.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False)

def handler_start_menu(message):
    if message.text == 'Меню🍕':
        show_menu(message)
    elif message.text[0:7] == 'Корзина':
        show_cart(message)
    else:
        bot.send_message(message.chat.id, 'Выберите кнопку', reply_markup=bot_start_menu())


def show_menu(message):
    bot.send_message(message.chat.id, 'Меню', reply_markup=create_menu())

def show_cart(message):
    bot.send_message(message.chat.id, 'Корзина', reply_markup=create_cart())


def bot_start_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton('Меню🍕')
    btn2 = types.KeyboardButton('Корзина🧺')
    markup.add(btn1, btn2)
    return markup


def create_menu(page=0):
    markup = types.InlineKeyboardMarkup()
    start_index = page * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE
    with open('products.json', 'r', encoding='utf-8') as file:
        products_list = json.load(file)
        for product in products_list['menu_items'][start_index:end_index]:
            callback_data = f'item:{product["name"]}'
            button = types.InlineKeyboardButton(text=product['name'], callback_data=callback_data)
            markup.add(button)
        if page > 0:
            btn1 = types.InlineKeyboardButton(text='<<', callback_data=f'page:{page-1}')
            markup.add(btn1)
        if end_index < len(products_list['menu_items']):
            btn2 = types.InlineKeyboardButton(text='>>', callback_data=f'page:{page+1}')
            markup.add(btn2)
    return markup


def create_cart():
    if cart_items:
        markup = types.InlineKeyboardMarkup()
        price = 0
        temp_cart = cart_items
        for item in cart_items:
            producttype = 0
            for item2 in cart_items:
                if item == item2:
                    producttype += 1
                    temp_cart.remove(item2)

            callback_data = f'item:{item["name"]}'
            button = types.InlineKeyboardButton(text=f'{item["name"]} x{producttype} - {int(item["price"].split(" ")[0])*producttype}', callback_data=callback_data)
            markup.add(button)
            price += int(item["price"].split(' ')[0])
        total = types.InlineKeyboardButton(text=f'Итого: {price} руб', callback_data='dataprice')
        markup.add(total)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button = types.KeyboardButton(text='Корзина пуста')
        markup.add(button)
    return markup


def add_to_cart(name, price):
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Добавить в корзину', callback_data=f'add_cart:{name}:{price}')
    markup.add(button)
    return markup


def to_cart():
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Перейти в корзину', callback_data=f'to_cart:')
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
                    bot.send_photo(call.message.chat.id, photo, caption=f'{chosen_product},\n{product["price"]}', reply_markup=add_to_cart(product["name"], product["price"]))
    elif call.data.startswith('add_cart:'):
        name, price = call.data.split(':')[1], call.data.split(':')[2]

        # bot.edit_message_text(text='Удалить из корзины', message_id=call.message.message_id)
        item = {
            "name": name,
            "price": price
        }
        cart_items.append(item)
        bot.send_message(call.message.chat.id, 'Добавлено в корзину', reply_markup=to_cart())
    elif call.data.startswith('to_cart:'):
        show_cart(call.message)
    elif call.data.startswith('page:'):
        text, page = call.data.split(':')
        markup = create_menu(int(page))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Меню:', reply_markup=markup)

if __name__ == "__main__":
    bot.polling(none_stop=True)
