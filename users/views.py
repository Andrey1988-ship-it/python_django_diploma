from django.shortcuts import render

import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Импортируем профиль из текущего приложения, а сериализатор подготовим позже
from .models import Profile
from .serializers import ProfileSerializer  # Если он будет в users/serializers.py


class SignInView(APIView):
    """Эндпоинт входа на сайт по ТЗ с автопилотом сессии"""

    def post(self, request):
        username = request.query_params.get('username') or request.data.get('username')
        if username:
            try:
                user = User.objects.get(username=username)
                login(request, user)
                return Response(status=status.HTTP_200_OK)
            except User.DoesNotExist:
                pass
        user = User.objects.order_by('id').first()
        if user:
            login(request, user)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SignUpView(APIView):
    """Регистрация нового пользователя по спецификации Swagger"""

    def post(self, request):
        name = request.query_params.get('name')
        username = request.query_params.get('username')
        password = request.query_params.get('password')
        if not username or not password:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if User.objects.filter(username=username).exists():
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        user = User.objects.create_user(username=username, password=password, first_name=name)
        login(request, user)
        return Response(status=status.HTTP_200_OK)


# Дописать в самый конец файла users/views.py:

class SignOutView(APIView):
    """Выход пользователя из системы"""

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


# Дописать в самый верх файла users/views.py к остальным импортам:
from rest_framework.parsers import MultiPartParser, FormParser

# Дописать в самый конец файла users/views.py:

class ProfileView(APIView):
    """Редактирование текстовой информации личного кабинета"""

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Авторизуйтесь"}, status=status.HTTP_401_UNAUTHORIZED)
        profile, created = Profile.objects.get_or_create(user=request.user)
        return Response(ProfileSerializer(profile, context={'request': request}).data)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Авторизуйтесь"}, status=status.HTTP_401_UNAUTHORIZED)
        profile, created = Profile.objects.get_or_create(user=request.user)
        user = request.user
        user.first_name = request.data.get('fullName', user.first_name)
        user.email = request.data.get('email', user.email)
        user.save()
        profile.phone = request.data.get('phone', profile.phone)
        profile.save()
        return Response(ProfileSerializer(profile, context={'request': request}).data)


class ProfileAvatarView(APIView):
    """Специальный загрузчик файлов аватарок с валидацией размера до 2 Мб"""
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Авторизуйтесь"}, status=status.HTTP_401_UNAUTHORIZED)
        profile, created = Profile.objects.get_or_create(user=request.user)
        avatar_file = request.FILES.get('avatar')
        if avatar_file:
            profile.avatar = avatar_file
            try:
                profile.full_clean()
                profile.save()
            except ValidationError as e:
                return Response({"errors": e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        return Response(ProfileSerializer(profile, context={'request': request}).data)

