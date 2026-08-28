import json
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth import authenticate, login, logout
from .models import Profile
from .serializers import UserProfileSerializer

class RegisterView(APIView):
    def get(self, request):
        return Response({"message": "Используйте метод POST для регистрации"}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        if isinstance(data, dict) and len(data) == 1:
            key = list(data.keys())[0]
            if key.startswith('{'):
                try:
                    data = json.loads(key)
                except:
                    pass
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
        return Response({"message": "Пользователь успешно зарегистрирован"}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def get(self, request):
        return Response({"message": "Используйте метод POST для входа"}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        if isinstance(data, dict) and len(data) == 1:
            key = list(data.keys())[0]
            if key.startswith('{'):
                try:
                    data = json.loads(key)
                except:
                    pass
        username = data.get('username') or data.get('name') or data.get('email')
        password = data.get('password')

        user = authenticate(request=request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"message": "Вход выполнен"}, status=status.HTTP_200_OK)
        return Response({"error": "Неверные данные"}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Вы вышли из системы"}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def get(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"error": "Авторизуйтесь"}, status=status.HTTP_401_UNAUTHORIZED)
        Profile.objects.get_or_create(user=user)
        serializer = UserProfileSerializer(user, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"error": "Авторизуйтесь"}, status=status.HTTP_401_UNAUTHORIZED)
        profile, _ = Profile.objects.get_or_create(user=user)

        data = request.data
        if isinstance(data, dict) and len(data) == 1:
            key = list(data.keys())[0]
            if key.startswith('{'):
                try:
                    data = json.loads(key)
                except:
                    pass

        # Обработка ФИО: фронт шлёт fullName
        full_name = data.get('fullName')
        if full_name:
            parts = full_name.split()
            if parts:
                user.first_name = parts[0]
            if len(parts) > 1:
                user.last_name = ' '.join(parts[1:])
        else:
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']

        if 'email' in data:
            user.email = data['email']
        if 'phone' in data:
            profile.phone = data['phone']

        # Обработка аватара, если он пришёл в этом же запросе
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']

        user.save()
        profile.save()

        serializer = UserProfileSerializer(user, context={'request': request})
        return Response(serializer.data)


class AvatarView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"error": "Авторизуйтесь"}, status=status.HTTP_401_UNAUTHORIZED)
        profile, _ = Profile.objects.get_or_create(user=user)

        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
            profile.save()
            # Возвращаем обновлённые данные профиля, чтобы фронт сразу обновил картинку
            serializer = UserProfileSerializer(user, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Файл не найден"}, status=status.HTTP_400_BAD_REQUEST)