import json
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2 import Error

load_dotenv(
    os.path.join(
        Path(Path(__file__).resolve().parent.parent.parent),
        '.env'
    )
)
print(Path(Path(__file__).resolve().parent.parent))
DB_NAME = (os.getenv('DB_NAME'))
POSTGRES_USER = (os.getenv('POSTGRES_USER'))
POSTGRES_PASSWORD = (os.getenv('POSTGRES_PASSWORD'))
DB_HOST = (os.getenv('DB_HOST'))
DB_PORT = (os.getenv('DB_PORT'))

try:
    connection = psycopg2.connect(
        dbname=DB_NAME,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )
    cursor = connection.cursor()
    data = json.load(open(
        './data/ingredients.json',
        'r',
        encoding='utf8',
    ))
    for str in data:
        cursor.execute(
            f"INSERT INTO recipes_ingredient("
            f"name, measurement_unit)"
            f"VALUES ('{str.get('name')}', '{str.get('measurement_unit')}');")
    connection.commit()
    print('Данные успешно внесены в базу данны PostgreSQL')
except (Exception, Error) as err:
    print("Ошибка при работе с PostgreSQL", err)
finally:
    if connection:
        cursor.close()
        connection.close()
        print("Соединение с PostgreSQL закрыто")
