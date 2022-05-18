from configs import database, cursor


def create_categories():
    cursor.execute('DROP TABLE IF EXISTS categories CASCADE;')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories(
        category_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        category_title VARCHAR(50) NOT NULL UNIQUE
    );
    ''')


def create_products():
    cursor.execute('DROP TABLE IF EXISTS products CASCADE;')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products(
        product_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        product_title VARCHAR(255),
        brand VARCHAR(255),
        link TEXT,
        price TEXT,
        image TEXT,
        characteristics TEXT,
        category_id INTEGER NOT NULL,
        UNIQUE(product_title, link),
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
    );
    ''')


def create_users():  # user_id telegram_id first_name username phone
    cursor.execute('DROP TABLE IF EXISTS users CASCADE;')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        telegram_id INTEGER NOT NULL UNIQUE,
        first_name VARCHAR(50),
        username VARCHAR(50),
        phone VARCHAR(30) 
    );
    ''')


def create_cart():
    cursor.execute('DROP TABLE IF EXISTS cart CASCADE;')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cart(
        cart_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        user_id INTEGER NOT NULL UNIQUE,
        total_quantity INTEGER DEFAULT 0,
        total_price INTEGER DEFAULT 0,
        
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );
    ''')


def create_cart_products():
    cursor.execute('DROP TABLE IF EXISTS cart_products CASCADE;')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cart_products(
        cart_product_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        cart_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER DEFAULT 1,
        price INTEGER,
        
        FOREIGN KEY (cart_id) REFERENCES cart(cart_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id),
        UNIQUE(cart_id, product_id)
    );
    ''')


create_categories()
create_users()
create_products()
create_cart()
create_cart_products()

database.commit()
database.close()
