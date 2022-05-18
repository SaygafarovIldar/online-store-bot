# TODO Сделать приветствие
# TODO Сделать вывод категорий товаров
# TODO Сделать страницы показа товаров и кнопку подробнее
# TODO Реализовать сообщение "Подробнее" и инлайн кнопки
# TODO Реализовать корзину пользователя и логику покупки
# TODO Реализовать регистрацию в момент первой покупки
# TODO Сделать кнопку с историей покупок
# TODO Сделать админский доступ с возможностью добавления и удаления товаров и категорий
# TODO Поиск по названию телефона
# TODO Поиск по цене в диапазоне
# TODO реализовать рассылку всем подписчикам бота при появлении нового телефона в асортименте
from telebot import TeleBot
from configs import *
from functions import *
from keyboards import *
from telebot.types import LabeledPrice

database = sql.connect(
    database='onlineStore',
    host='localhost',
    user='postgres',
    password='123456'
)

cursor = database.cursor()

bot = TeleBot(TOKEN, parse_mode='HTML')


@bot.message_handler(commands=['start', 'help', 'admin'])
def command_start(message):
    chat_id = message.chat.id
    if message.text == '/start':
        msg = bot.send_message(chat_id, f'''Здравствуйте, <b>{message.from_user.first_name}</b>
        
<i>Добро пожаловать в наш онлайн магазин.</i>
Здесь вы найдете самый 
широкий ассортимент товаров.

<i>Что желаете сделать?</i> 
Посмотреть товары без регистрации?
Или <b>зарегистрироваться?</b>''', reply_markup=start_buttons())
        bot.register_next_step_handler(msg, choose)

    elif message.text == '/help':
        bot.send_message(chat_id, '''Данный бот был создан при поддержке <b>PROWEB</b>.
При создании этого бота ни один студент не пострадал
При каких либо неполадках или вопросах напишите сюда:
<b>@FomichevEvgeniy</b>
Для продолжения нажмите /start''')
    elif message.text == '/admin':
        msg = bot.send_message(chat_id, f'''Добро пожаловать администратор <b>{message.from_user.first_name}</b>''',
                               reply_markup=admin_buttons())
        bot.register_next_step_handler(msg, choose)


def choose(message):
    chat_id = message.chat.id
    if message.text == 'Посмотреть товары':
        show_categories(message)
    elif message.text == 'Зарегистрироваться':
        register(message)
    elif message.text == 'Добавить категорию':
        add_category(message)
    elif message.text == 'Добавить товар':
        add_product(message)
    elif message.text == 'Удалить категорию':
        delete_category(message)
    elif message.text == 'Удалить товар':
        delete_product(message)
    elif message.text == 'Выйти из панели админа':
        msg = bot.send_message(chat_id, f'''Здравствуйте, <b>{message.from_user.first_name}</b>

<i>Добро пожаловать в наш онлайн магазин.</i>
Здесь вы найдете самый 
широкий ассортимент товаров.

<i>Что желаете сделать?</i> 
Посмотреть товары без регистрации?
Или <b>зарегистрироваться?</b>''', reply_markup=start_buttons())
        bot.register_next_step_handler(msg, choose)


def show_categories(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, 'Выберите категорию', reply_markup=generate_categories())
    bot.register_next_step_handler(msg, show_category_info)


def register(message):
    chat_id = message.chat.id

    cursor.execute('''
    SELECT * FROM users WHERE telegram_id = %s;
    ''', (chat_id,))

    user = cursor.fetchone()

    if user:
        bot.send_message(chat_id, 'Вы уже зарегестрированы в системе!')
        show_categories(message)

    else:
        try:
            phone = message.contact.phone_number
            first_name = message.from_user.first_name
            username = message.from_user.username

            # Регистрация
            cursor.execute('''
                INSERT INTO users (telegram_id, first_name, username, phone) VALUES (%s, %s, %s, %s)
                ON CONFLICT (telegram_id) DO NOTHING
                ''', (chat_id, first_name, username, phone))

            cursor.execute('''
            INSERT INTO cart(user_id)
            SELECT user_id FROM users WHERE telegram_id = %s
            ON CONFLICT(user_id) DO NOTHING
            ''', (chat_id,))

            database.commit()

            show_categories(message)
        except Exception as e:
            msg = bot.send_message(chat_id, 'Для регистрации нажмите на кнопку!', reply_markup=generate_phone_number())
            bot.register_next_step_handler(msg, register)


@bot.message_handler(regexp=r'[а-яА-Яё ]+')
def show_category_info(message):
    chat_id = message.chat.id
    category_name = message.text
    if 'корзина' in category_name.lower():
        show_cart(message)  # TODO Запускать функцию корзины
    if category_name in CATEGORIES:
        category_id = CATEGORIES[category_name]['category_id']
        cursor.execute('''
        SELECT COUNT(*) FROM products WHERE category_id = %s;
        ''', (category_id,))
        DATA['count_products'] = cursor.fetchone()[0]
        DATA['total_pages'] = get_total_pages(DATA['count_products'], MAX_QUANTITY)
        DATA['category_name'] = category_name

        """Получаем всю информацию о товарах"""
        cursor.execute('''
        SELECT product_id, product_title, price FROM products
        WHERE category_id = %s
        ''', (category_id,))
        DATA['products'] = cursor.fetchall()

        if DATA['products']:
            pagination_products(message)
        else:
            bot.send_message(chat_id, 'Ничего не найдено, попробуйте еще',
                             reply_markup=generate_categories())


def pagination_products(message):
    chat_id = message.chat.id
    user_text = f'Список продуктов в категории {DATA["category_name"]} \n\n'
    i = 1
    for product in DATA['products'][0:MAX_QUANTITY]:
        product_id = product[0]
        product_title = product[1]
        product_price = product[2]

        user_text += f'''{i}. {product_title}
Стоимость: {product_price}
Подробнее: /product_{product_id}\n\n'''
        i += 1
    bot.send_message(chat_id, user_text, reply_markup=generate_pagination(DATA['total_pages']))


@bot.callback_query_handler(func=lambda call: call.data.isdigit())
def answer_page_call(call):
    chat_id = call.message.chat.id
    message_id = call.message.id
    current_page = int(call.data)

    try:
        user_text = f'Список продуктов в категории {DATA["category_name"]} \n\n'
        start = (current_page - 1) * MAX_QUANTITY
        last_index = current_page * MAX_QUANTITY
        end = last_index if last_index <= DATA['count_products'] else DATA['count_products']

        for i in range(start, end):
            product_id = DATA['products'][i][0]
            product_title = DATA['products'][i][1]
            product_price = DATA['products'][i][2]

            user_text += f'''{i}. {product_title}
Стоимость: {product_price}
Подробнее: /product_{product_id}\n\n'''

        bot.edit_message_text(text=user_text,
                              chat_id=chat_id,
                              message_id=message_id,
                              reply_markup=generate_pagination(DATA['total_pages'], current_page))
        bot.answer_callback_query(call.id, show_alert=False)
    except:
        bot.answer_callback_query(call.id, 'Текущая страница')


@bot.message_handler(regexp=r'\/product_[0-9]+')
def show_product_details(message):  # /product_[12312]
    chat_id = message.chat.id
    _, product_id = message.text.split('_')
    cursor.execute(
        '''
        SELECT product_title, brand, link, price, image,characteristics FROM products
        WHERE product_id = %s;
        ''', (product_id,)
    )

    product = cursor.fetchone()
    if product:
        title = product[0]
        brand = product[1]
        link = product[2]
        price = product[3]
        image = product[4]
        characteristics = product[5]

        msg_for_user = f'''<b>{title}</b>
<b>{brand}</b>
<b>Описание товара</b>
<i>{characteristics}</i>
<b>Стоимость:</b> {price}

'''
        markup = generate_detail_markup(link=link, product_id=product_id, price=price)
        bot.send_photo(chat_id=chat_id, photo=image, caption=msg_for_user, reply_markup=markup)
    else:
        bot.send_message(chat_id, 'Продукт не найден')


@bot.callback_query_handler(func=lambda call: 'add' in call.data)
def add_product_in_cart(call):
    _, product_id, product_price = call.data.split('_')
    chat_id = call.message.chat.id

    # Получение данных о корзине

    cursor.execute('''
    SELECT cart_id FROM cart WHERE user_id = (
    SELECT user_id FROM users WHERE telegram_id = %s
    );
    ''', (chat_id,))

    cart_id = cursor.fetchone()
    product_price = product_price.replace(' ', '').replace('cум', '')  # 1550500

    cursor.execute('''
    INSERT INTO cart_products(cart_id, product_id, price)
    VALUES ( %(cart_id)s, %(product_id)s, %(price)s )
    ON CONFLICT (cart_id, product_id) DO UPDATE
    SET price = cart_products.price + %(price)s,
    quantity = cart_products.quantity + 1
    WHERE cart_products.cart_id = %(cart_id)s 
    AND cart_products.product_id = %(product_id)s;
    
    UPDATE cart
    SET total_price = info.total_price,
    total_quantity = info.total_quantity
    
    FROM (
    SELECT SUM(quantity) as total_quantity,
    SUM(price) as total_price FROM cart_products
    WHERE cart_id = %(cart_id)s
    ) as info;
    ''', {
        'cart_id': cart_id,
        'product_id': product_id,
        'price': product_price
    })

    database.commit()
    bot.answer_callback_query(callback_query_id=call.id, text='Добавлено')


@bot.message_handler(func=lambda message: 'корзина' in message.text.lower())
def show_cart(message):
    chat_id = message.chat.id
    """Получение всех продуктов пользователя"""

    cursor.execute('''
        SELECT product_title, cart_products.quantity,
        cart_products.price FROM cart_products
        JOIN products USING(product_id)
        
        WHERE cart_id = (SELECT cart_id FROM cart WHERE user_id = (
            SELECT user_id FROM users WHERE telegram_id = %s)
        )
    ''', (chat_id,))
    products = cursor.fetchall()

    cursor.execute('''
    SELECT cart_id, total_price, total_quantity FROM cart
    WHERE user_id = (SELECT user_id FROM users WHERE telegram_id = %s)
    ''', (chat_id,))

    cart_id, total_price, total_quantity = cursor.fetchone()

    cart_text = 'Ваша корзина.\n'

    i = 0
    for title, quantity, price in products:
        i += 1
        cart_text += f'''{i}. <b>{title}</b>
Кол-во: {quantity}
Стоимость: {price} сум \n\n'''

    cart_text += f'''<i>Общее кол-во товаров в корзине: {total_quantity}</i>
<i>Общая стоимость товаров: {total_price} сум</i>
Очистить корзину - /clear_cart'''

    bot.send_message(chat_id, cart_text, reply_markup=generate_pay_menu(cart_id))


@bot.message_handler(commands=['clear_cart'])
def clean_cart(message):
    cursor.execute('''
    DELETE FROM cart_products WHERE
    cart_id = (SELECT cart_id FROM cart WHERE user_id = 
    (SELECT user_id FROM users WHERE telegram_id = %s)
    );
    UPDATE cart
    SET total_price = 0,
    total_quantity = 0;
    ''', (message.chat.id,))
    database.commit()
    bot.send_message(message.chat.id, 'Корзина очищена!')


@bot.callback_query_handler(func=lambda call: 'pay' in call.data)
def pay_cart(call):
    _, cart_id = call.data.split('_')
    chat_id = call.message.chat.id

    cursor.execute(
        '''
        SELECT total_price FROM cart WHERE cart_id = %s;
        ''', (cart_id,)
    )
    total_price = int(cursor.fetchone()[0])
    cursor.execute('''
           SELECT product_title, cart_products.quantity,
           cart_products.price FROM cart_products
           JOIN products USING(product_id)
           WHERE cart_id = %s
       ''', (cart_id,))
    products = cursor.fetchall()

    cart_text = 'Вы выбрали: \n'

    i = 0
    for title, quantity, price in products:
        i += 1
        cart_text += f'''{i}. {title}
    Кол-во: {quantity}
    Стоимость: {price} сум \n\n'''

        try:
            bot.send_invoice(chat_id=chat_id,
                             title='Ваша корзина',
                             description=cart_text,
                             invoice_payload='bot-defined invoice payload',
                             provider_token='371317599:TEST:1638446514048',
                             currency='UZS',
                             prices=[LabeledPrice(label='Корзина', amount=int(str(total_price) + '00'))],
                             start_parameter='pay',
                             is_flexible=False
                             )



        except Exception:
            bot.send_message(chat_id, 'Не удалось провести оплату')


def add_category(message):
    pass


def add_product(message):
    pass


def delete_category(message):
    pass


def delete_product(message):
    pass


bot.polling(none_stop=True)
