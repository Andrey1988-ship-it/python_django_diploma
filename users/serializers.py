from rest_framework import serializers
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source='profile.phone', required=False, allow_blank=True)
    avatar = serializers.SerializerMethodField()
    fullName = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'fullName', 'phone', 'avatar']

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.profile.avatar:
            url = obj.profile.avatar.url
            # Возвращаем объект, как ожидает фронт
            return {"src": request.build_absolute_uri(url) if request else url, "alt": "Аватар"}
        return {"src": "", "alt": "Аватар"}

    def get_fullName(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()