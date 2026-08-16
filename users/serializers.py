from rest_framework import serializers
# Импортируем модель профиля из текущего приложения users
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
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
                "alt": "avatar",
                "width": "150",
                "height": "150"
            }
        return {"src": "https://placeholder.com", "alt": "default avatar"}
