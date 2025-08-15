# users/serializers.py
from rest_framework import serializers
from .models import User

# ====== Read ======
class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id", "username", "name", "email", "phone",
            "province_name", "city_name",
            "avatar_url", "gender", "age_band", "intro",
            "manner_temperature",
        )

# ====== Write (요청 바디 검증용) ======
class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=40)
    name = serializers.CharField(max_length=40, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    def validate_username(self, v):
        if User.objects.filter(username=v).exists():
            raise serializers.ValidationError("이미 사용 중인 아이디입니다.")
        return v

class SetLocationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    province_name = serializers.CharField(max_length=20, required=False, allow_blank=True)
    city_name = serializers.CharField(max_length=40, required=False, allow_blank=True)

class CreateCardSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    avatar_url = serializers.URLField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=30)
    gender = serializers.ChoiceField(choices=["male","female","other"], required=False, allow_blank=True)
    age_band = serializers.ChoiceField(choices=["10s","20s","30s","40s","50s","60s+"], required=False, allow_blank=True)
    intro = serializers.CharField(required=False, allow_blank=True, max_length=500)
    name = serializers.CharField(required=False, allow_blank=True, max_length=40)
    email = serializers.EmailField(required=False, allow_blank=True)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    def validate(self, attrs):
        if not attrs.get("username") and not attrs.get("email"):
            raise serializers.ValidationError("username 또는 email 중 하나는 필요합니다.")
        return attrs

class UpdateMeSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True, max_length=40)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=30)
    avatar_url = serializers.URLField(required=False, allow_blank=True)
    gender = serializers.ChoiceField(choices=["male","female","other"], required=False, allow_blank=True)
    age_band = serializers.ChoiceField(choices=["10s","20s","30s","40s","50s","60s+"], required=False, allow_blank=True)
    intro = serializers.CharField(required=False, allow_blank=True, max_length=500)
    province_name = serializers.CharField(required=False, allow_blank=True, max_length=20)
    city_name = serializers.CharField(required=False, allow_blank=True, max_length=40)

class MannerUpdateSerializer(serializers.Serializer):
    manner_temperature = serializers.IntegerField(min_value=0, max_value=100)
