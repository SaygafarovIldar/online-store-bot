import psycopg2 as sql

CATEGORIES ={
    'Оптимальные смартфоны': {
        'page_name': 'optimal-smartfony',
        'category_id': 1
    },
    'Игровые смартфоны': {
        'page_name': 'gaming-smartfony',
        'category_id': 2
    },
    'Флагманы': {
        'page_name': 'premium-smartfony',
        'category_id': 3
    }
}


TOKEN = '5071151152:AAE_8C6_-uHjhY9R8IALmK9T-N-WaWyIu3I'

DATA = {}

PAYME_TOKEN = ''

MAX_QUANTITY = 3

database = sql.connect(
    database='onlineStore',
    host='localhost',
    user='postgres',
    password='123456'
)

cursor = database.cursor()

