# Файл створено з допомогою Gemini

import psycopg2
from psycopg2.extras import execute_values
from faker import Faker
import random

# налаштування підключення
conn = psycopg2.connect(
    dbname="tabletop",
    user="postgres",
    password="1234",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()
fake = Faker()

def seed_data():
    categories = [("Стратегії",), ("Сімейні",), ("Для вечірок",), ("РПГ",)]
    execute_values(cursor, "insert into categories (name) values %s", categories)
    
    cursor.execute("select id from categories")
    cat_ids = [row[0] for row in cursor.fetchall()]
    games_data = [(f"Гра {fake.word()}", round(random.uniform(300, 3000), 2), random.choice(cat_ids)) for _ in range(50)]
    execute_values(cursor, "insert into games (title, price, category_id) values %s", games_data)
    
    print("Генеруємо клієнтів...")
    customers_data = [(fake.unique.email(), fake.name()) for _ in range(10000)]
    execute_values(cursor, "insert into customers (email, name) values %s", customers_data)
    
    print("Генеруємо замовлення...")
    cursor.execute("select id from customers")
    cust_ids = [row[0] for row in cursor.fetchall()]
    orders_data = [(random.choice(cust_ids), fake.date_between(start_date='-2y', end_date='today')) for _ in range(100000)]
    execute_values(cursor, "insert into orders (customer_id, order_date) values %s", orders_data)
    
    print("Генеруємо позиції замовлень (500k рядків)...")
    cursor.execute("select id from orders")
    order_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute("select id from games")
    game_ids = [row[0] for row in cursor.fetchall()]
    
    items_data = []
    for _ in range(500000):
        items_data.append((random.choice(order_ids), random.choice(game_ids), random.randint(1, 5)))
    
    execute_values(cursor, "insert into order_items (order_id, game_id, quantity) values %s on conflict do nothing", items_data)

    conn.commit()
    print("Генерацію завершено!")

if __name__ == "__main__":
    seed_data()
    cursor.close()
    conn.close()