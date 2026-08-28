from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Аватар")

    # Поле должно быть ВНУТРИ класса!
    is_deleted = models.BooleanField(default=False)  # <--- ИСПРАВЛЕНО

    def __str__(self):
        return f"Профиль: {self.user.username}"