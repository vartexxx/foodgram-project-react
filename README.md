### Проект Foodgram
![example workflow](https://github.com/vartexxx/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)
**Foodgram** - продуктовый помощник.

Пользователи могут публиковать рецептыб подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать в формате .txt список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

***

Проект развернут по IP [84.201.134.240](http://84.201.134.240/)

### Технологии

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)

### Инструкция для разворачивания проекта на удаленном сервере:

- Склонируйте проект из репозитория:

```sh
$ git clone https://github.com/vartexxx/foodgram-project-react.git
```

- Выполните вход на удаленный сервер

- Установите DOCKER на сервер по официальной доке.

- Установитe docker-compose на сервер:
```sh
sudo apt install docker-compose
```

- Отредактируйте конфигурацию сервера NGNIX:
```sh
измените файл ..infra/nginx.conf
```

- Скопируйте файлы docker-compose.yml и nginx.conf из директории ../infra/ на удаленный сервер, в домашнюю дерикторию:
```sh
scp docker-compose.yml <username>@<host>:
scp nginx.conf <username>@<host>:
```

- Создайте переменные окружения (пример указан в ../infra/env.example) и добавьте их в Secrets GitHub Actions:
```sh
nano .env
```

- Запустите приложение в контейнерах:

```sh
docker-compose up -d --build
```

- Выполните миграции:

```sh
docker-compose exec backend python manage.py migrate
```

- Создайте суперпользователя:

```sh
docker-compose exec backend python manage.py createsuperuser
```

- Выполните команду для сбора статики:

```sh
docker-compose exec backend python manage.py collectstatic --no-input
```

- Команда для остановки приложения в контейнерах:

```sh
docker-compose down -v
```

### Примеры использования API для неавторизованных пользователей:

```sh
GET /api/users/- получить список всех пользователей.
GET /api/tags/- получить список всех тегов.
GET /api/tags/{id}/ - получить тег по ID.
GET /api/recipes/- получить список всех рецептов.
GET /api/recipes/{id}/ - получить рецепт по ID.
GET /api/users/subscriptions/ - получить список всех пользователей, на которых подписан текущий пользователь. В выдачу добавляются рецепты.
GET /api/ingredients/ - получить список ингредиентов с возможностью поиска по имени.
GET /api/ingredients/{id}/ - получить ингредиент по ID.
```

### Автор
Бурлака Владислав