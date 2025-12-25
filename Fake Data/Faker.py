from faker import Faker
import mysql.connector
import random
from datetime import datetime, timedelta

fake = Faker('ru_RU')

connection = mysql.connector.connect(host='localhost',
                                     user= 'root',
                                     password='56g87h48',
                                     database='pizzeria')

cursor = connection.cursor()

delivery_types = ['Велокурьер', 'Пеший', 'Автокурьер']

for _ in range(8):
    cursor.execute("""
        INSERT INTO delivery (first_name, last_name, city, delivery_type)
        VALUES (%s, %s, %s, %s)
    """, (
        fake.first_name_male(),
        fake.last_name_male(),
        'Нижний Новгород',
        random.choice(delivery_types)
    ))

for _ in range(2):
    cursor.execute("""
    INSERT INTO delivery (first_name, last_name, city, delivery_type)
    VALUES (%s, %s, %s, %s)""",
                   (fake.first_name_female(),
                    fake.last_name_female(),
                    'Нижний Новгород',
                    random.choice(delivery_types)
                   ))

genders = ['Male', 'Female']

for _ in range(30):
    cursor.execute("""
        INSERT INTO customer (
            first_name, last_name, gender, birthday, reg_date,
            city, street, building, apartment
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        fake.first_name_male(),
        fake.last_name_male(),
        random.choice(genders),
        fake.date_of_birth(minimum_age=18, maximum_age=65),
        fake.date_time_between(start_date='-2d'),
        'Нижний Новгород',
        fake.street_name(),
        random.randint(1, 200),
        random.choice([None, random.randint(1, 100)])
    ))

for _ in range(30):
    cursor.execute("""
        INSERT INTO customer (
            first_name, last_name, gender, birthday, reg_date,
            city, street, building, apartment
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        fake.first_name_female(),
        fake.last_name_female(),
        random.choice(genders),
        fake.date_of_birth(minimum_age=18, maximum_age=65),
        fake.date_time_between(start_date='-2d'),
        'Нижний Новгород',
        fake.street_name(),
        random.randint(1, 200),
        random.choice([None, random.randint(1, 100)])
    ))


cursor.execute("SELECT id FROM customer")
customers = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT id FROM delivery")
deliveries = [row[0] for row in cursor.fetchall()]

statuses = ['Доставлен', 'Отменен', 'Обработка']

for _ in range(100):
    status = random.choice(statuses)

    cursor.execute("""
        INSERT INTO orders (customer_id, date_time, deliver_id, status)
        VALUES (%s, %s, %s, %s)
    """, (
        random.choice(customers),
        fake.date_time_between(start_date='-2d'),
        random.choice(deliveries) if status != 'Обработка' else None,
        status
    ))

cursor.execute("""
    INSERT INTO pizza_types (size, diameter, weight, calories, protein, fat, carbohydrates)
    VALUES
    ('Маленькая', 23, 7.99, 220, 9, 8, 28),
    ('Средняя', 32, 10.99, 260, 11, 10, 32),
    ('Большая', 41, 14.99, 300, 13, 12, 38)
""")

cursor.execute("SELECT id FROM pizza_types")
type_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("""
    INSERT INTO pizza (name, type_id) VALUES
    ('Маргарита', %s),
    ('Пепперони', %s),
    ('Гавайская', %s),
    ('4 сезона', %s),
    ('Мясная', %s)
""", (type_ids[0], type_ids[1], type_ids[2], type_ids[1], type_ids[2]))


statuses = ['Доставлен', 'Отменен', 'Обработка']

for _ in range(100):
    status = random.choice(statuses)
    cursor.execute("""
        INSERT INTO orders (customer_id, date_time, deliver_id, status)
        VALUES (%s, %s, %s, %s)
    """, (
        random.choice(customers),
        fake.date_time_between(start_date='-2y'),
        random.choice(deliveries) if status != 'Обработка' else None,
        status
    ))

# Получаем список id всех заказов
cursor.execute("SELECT id FROM orders")
orders = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT pizza_id, type_id FROM pizza")
pizzas = cursor.fetchall()  # [(pizza_id, type_id), ...]
for order_id in orders:
    pizzas_in_order = set()  # чтобы не дублировать пиццы
    for _ in range(random.randint(1, 4)):
        while True:
            pizza_id, type_id = random.choice(pizzas)
            if pizza_id not in pizzas_in_order:
                pizzas_in_order.add(pizza_id)
                break
        price = random.randint(400, 1300)
        cursor.execute("""
            INSERT INTO order_items (order_id, pizza_id, price, pizza_amount)
            VALUES (%s, %s, %s, %s)
        """, (order_id, pizza_id, price, random.randint(1,3)))

connection.commit()
cursor.close()
connection.close()