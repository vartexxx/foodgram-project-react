import json
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2 import Error

load_dotenv(
    os.path.join(
        Path(Path(__file__).resolve().parent.parent) / 'infra-dev',
        '.env'
    )
)
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
    json_file = open(
        './data/ingredients.json',
        'r',
        encoding='utf8',
    )
    data = json.load(json_file)
    for line in data:
        title = line.get('name')
        measurement_unit = line.get('measurement_unit')
        cursor.execute(
            f"INSERT INTO recipes_ingredientsmodel("
            f"name, measurement_unit"
            f") VALUES ('{title}', '{measurement_unit}');")
    connection.commit()
    cursor.close()
    connection.close()
    print('Данные успешно внесены в базу данны PostgreSQL')
except (Exception, Error) as error:
    print("Ошибка при работе с PostgreSQL", error)
