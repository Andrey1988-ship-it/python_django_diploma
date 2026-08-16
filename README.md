# Дипломный проект Django: Интернет-магазин

Проект представляет собой бэкенд-приложение на Django REST Framework, интегрированное с готовым фронтендом.

## Технологический стек
- Python 3.12
- Django 5.x
- Django REST Framework
- Celery / Redis (для отложенных задач)
- SQLite3 / PostgreSQL

## Как запустить проект локально

1. **Клонировать репозиторий и перейти в папку:**
   ```bash
   git clone -b Basalyga_market <https://gitlab.skillbox.ru/andrei_basalygo/python_django_diploma>
   cd PythonProject_fin
   ```

2. **Cоздать и активировать виртуальное окружение:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Для Linux/macOS
   # .venv\Scripts\activate   # Для Windows
   ```

3. **Установить зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Создать файл конфигурации `.env` в корне проекта и заполнить его:**
   ```env
   DEBUG=True
   SECRET_KEY=ваш_секретный_ключ_django
   ```

5. **Выполнить миграции базы данных:**
   ```bash
   python manage.py migrate
   ```

6. **Запустить локальный сервер:**
   ```bash
   python manage.py runserver
   ```
   Проект будет доступен по адресу: http://127.0.0
