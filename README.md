[![Django-app workflow](https://github.com/AllaStrigo/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/AllaStrigo/foodgram-project-react/actions/workflows/foodgram_workflow.yml)
# FoodGram
Сайт доступен по ссылке:[grocery-assistant](http://158.160.56.202)

## Описание
Проект "Продуктовый помошник" (Foodgram) предоставляет пользователям следующие возможности:
  - создание своих рецептов и управление ими
  - просмотр рецептов других пользователей
  - добавление рецептов в "Избранное" и/или в "Список покупок"
  - подписываться на других пользователей
  - скачивание списка ингредиентов для рецептов, добавленных в "Список покупок"

---

## Установка Docker (на платформе Ubuntu)
Для запуска необходимо установить Docker и Docker Compose. 
Подробнее об установке на других платформах можно узнать на [официальном сайте](https://docs.docker.com/engine/install/).

```bash
sudo apt update
```
```bash
sudo apt install docker.io
```
```bash
sudo apt install docker-compose
```
```bash
sudo systemctl start docker
```

---

## База данных и переменные окружения
Проект использует базу данных PostgreSQL. Для подключения и выполненя запросов к базе данных необходимо создать и заполнить файл ".env" с переменными окружения в папке "./infra/".

Шаблон для заполнения файла ".env":
```python
DB_ENGINE=django.db.backends.postgresql
DB_NAME='db_name'
POSTGRES_USER='postgres_user'
POSTGRES_PASSWORD='postgres_password'
DB_HOST='db'
DB_PORT=5432
SECRET_KEY='Здесь указать секретный ключ'
ALLOWED_HOSTS='Здесь указать имя или IP хоста'
```
---

## Команды для запуска

Необходимо склонировать проект. Cоздать и активировать виртуальное окружение:
```bash
python -m venv venv
```
```bash
Linux: source venv/bin/activate
Windows: source venv/Scripts/activate
```

И установить зависимости из файла requirements.txt:
```bash
python3 -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```

Далее необходимо собрать образы для фронтенда и бэкенда.  
Из папки "./infra/" выполнить команду:
```bash
docker-compose up
```

После успешного запуска контейнеров выполнить миграции:
```bash
docker-compose exec backend python manage.py makemigrations
```
```bash
docker-compose exec backend python manage.py migrate
```

Создать суперюзера (Администратора):
```bash
docker-compose exec backend python manage.py createsuperuser
```

Собрать статику:
```bash
docker-compose exec backend python manage.py collectstatic --no-input
```

Теперь доступность проекта можно проверить по адресу [http://localhost/](http://localhost/)

---
## Заполнение базы данных

С проектом поставляются данные об ингредиентах. Заполнить базу данных ингредиентами можно выполнив следующую команду:
```bash
docker-compose exec backend python manage.py ingredient_create
```
```bash
docker-compose exec backend python manage.py tegs_create
```
---