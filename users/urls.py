from django.urls import path
from .views import RegisterView, LoginView, LogoutView

urlpatterns = [
    # Регистрация
    path('sign-up', RegisterView.as_view(), name='sign-up'),
    path('sign-up/', RegisterView.as_view(), name='sign-up-slash'),

    # Авторизация
    path('sign-in', LoginView.as_view(), name='sign-in'),
    path('sign-in/', LoginView.as_view(), name='sign-in-slash'),

    # Выход
    path('logout', LogoutView.as_view(), name='logout'),
    path('logout/', LogoutView.as_view(), name='logout-slash'),
    path('sign-out', LogoutView.as_view(), name='sign-out'),
    path('sign-out/', LogoutView.as_view(), name='sign-out-slash'),
]