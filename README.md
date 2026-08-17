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

4. **Создать файл конфигурации `.env` в корне проекта и заполнить его по образцу:**
   * Скопируйте структуру из файла `.env.example` или создайте файл `.env` вручную.
   * Укажите следующие обязательные переменные:
     - `DEBUG` — режим отладки (поставьте `True` для разработки).
     - `SECRET_KEY` — секретный ключ вашего Django-проекта.
     - `CELERY_BROKER_URL` — URL-адрес брокера очередей Redis (например, `redis://127.0.0.1:6379/0`).
     - `CELERY_RESULT_BACKEND` — URL-адрес хранилища результатов Redis (например, `redis://127.0.0.1:6379/0`).

   **Пример готового файла `.env`:**
   ```env
   DEBUG=True
   SECRET_KEY=django-insecure-qe_sj$fj1a##ajz8_!f7a#me#wu)f22)t*40&v@4diz@ret-o8
   CELERY_BROKER_URL=redis://127.0.0.1:6379/0
   CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
   ```


5. **Выполнить миграции базы данных:**
   ```bash
   python manage.py migrate
   ```

6. **Запустить локальный сервер:**
   ```bash
   python manage.py runserver
   ```
   
