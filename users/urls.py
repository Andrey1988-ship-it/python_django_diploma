from django.urls import path
from .views import RegisterView, LoginView, LogoutView, ProfileView, AvatarView

urlpatterns = [
    path('sign-up', RegisterView.as_view(), name='sign-up'),
    path('sign-up/', RegisterView.as_view(), name='sign-up-slash'),
    path('sign-in', LoginView.as_view(), name='sign-in'),
    path('sign-in/', LoginView.as_view(), name='sign-in-slash'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('logout/', LogoutView.as_view(), name='logout-slash'),
    path('sign-out', LogoutView.as_view(), name='sign-out'),
    path('sign-out/', LogoutView.as_view(), name='sign-out-slash'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('profile/', ProfileView.as_view(), name='profile-slash'),
    path('profile/avatar', AvatarView.as_view(), name='profile-avatar'),
    path('profile/avatar/', AvatarView.as_view(), name='profile-avatar-slash'),
]