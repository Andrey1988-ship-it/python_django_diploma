import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


# Вспомогательная функция, чтобы распарсить странный JSON от Megano
def parse_megano_data(request):
    data = request.data
    # Если пришёл словарь с одним ключом, где ключ - это строка JSON
    if isinstance(data, dict) and len(data) == 1:
        key = list(data.keys())[0]
        if key.startswith('{'):
            try:
                data = json.loads(key)
                print(f"✅ JSON распарсен: {data}")
            except json.JSONDecodeError:
                pass
    # Дополнительная защита: если данные в сыром теле
    if not isinstance(data, dict) or not data.get('password'):
        try:
            raw_data = json.loads(request.body)
            if isinstance(raw_data, dict):
                data = raw_data
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
    return data


class RegisterView(APIView):
    def get(self, request):
        return Response({"message": "Используйте метод POST для регистрации"}, status=status.HTTP_200_OK)

    def post(self, request):
        data = parse_megano_data(request)
        print(f"🛠 Данные для регистрации: {data}")

        username = data.get('username') or data.get('name') or data.get('email')
        password = data.get('password')
        email = data.get('email', '')
        first_name = data.get('first_name') or data.get('firstName') or ''
        last_name = data.get('last_name') or data.get('lastName') or ''

        if not password:
            return Response({"error": "Пароль не указан"}, status=status.HTTP_400_BAD_REQUEST)

        if not username and email:
            username = email
        elif not username:
            return Response({"error": "Логин не указан"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Пользователь уже существует"}, status=status.HTTP_400_BAD_REQUEST)

        User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        print(f"✅ Пользователь {username} успешно создан!")
        return Response({"message": "Пользователь успешно зарегистрирован"}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def get(self, request):
        return Response({"message": "Используйте метод POST для входа"}, status=status.HTTP_200_OK)

    def post(self, request):
        data = parse_megano_data(request)
        print(f"🛠 Данные для входа: {data}")

        username = data.get('username') or data.get('name') or data.get('email')
        password = data.get('password')

        # Проверяем пользователя и создаем сессию
        user = authenticate(request=request, username=username, password=password)

        if user is not None:
            login(request, user)  # ВАЖНО: создаем сессию, чтобы шапка обновилась
            print(f"✅ Вход выполнен для: {username}")
            return Response({"message": "Вход выполнен"}, status=status.HTTP_200_OK)

        print(f"❌ Ошибка входа: пользователь {username} не найден или пароль неверный")
        return Response({"error": "Неверные данные"}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request):
        logout(request)  # Удаляем сессию
        return Response({"message": "Вы вышли из системы"}, status=status.HTTP_200_OK)