from django.db import migrations
from django.contrib.auth.models import User

def create_mandatory_data(apps, schema_editor):
    # По ТЗ: автоматическое создание администратора при разворачивании проекта
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='123', # Простой пароль для быстрой проверки куратором
            first_name='Администратор'
        )
        print("\n👶 [DATA MIGRATION] Суперпользователь 'admin' с паролем '123' успешно создан!")

    # Роли пользователей на сайте по ТЗ (можно расширить через группы)
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Администратор')
    Group.objects.get_or_create(name='Покупатель')
    print("👶 [DATA MIGRATION] Роли пользователей успешно инициализированы!")

def remove_mandatory_data(apps, schema_editor):
    # Логика отката миграции назад (по ТЗ миграции должны корректно отменяться)
    User.objects.filter(username='admin').delete()
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['Администратор', 'Покупатель']).delete()

class Migration(migrations.Migration):

    dependencies = [

        ('api', '0004_productimage'),
    ]

    operations = [
        migrations.RunPython(create_mandatory_data, remove_mandatory_data),
    ]

