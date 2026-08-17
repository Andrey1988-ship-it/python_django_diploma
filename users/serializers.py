from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    # Явно связываем поля с моделью User, так как фронтенд ждет fullName и email в одном объекте
    fullName = serializers.CharField(source='user.first_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['fullName', 'email', 'phone', 'avatar']

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            url = request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url
            return {
                "src": url,
                "alt": "avatar"
            }
        return {"src": "https://placeholder.com", "alt": "default avatar"}
