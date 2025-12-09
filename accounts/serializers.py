# accounts/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers

from access_control.models import Role, UserRole

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
            "middle_name",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password2")

        email = validated_data.get("email")

        # username обязателен для AbstractUser — подставим email
        if "username" in [f.name for f in User._meta.fields]:
            validated_data.setdefault("username", email)

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Роль по умолчанию — "user"
        role, _ = Role.objects.get_or_create(
            name="user",
            defaults={"description": "Обычный пользователь"},
        )
        UserRole.objects.create(user=user, role=role)

        return user


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "middle_name", "role")

    def get_role(self, obj):
        user_role = getattr(obj, "user_role", None)
        if user_role and user_role.role:
            return user_role.role.name
        return None


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Неверный email или пароль")

        if not user.is_active:
            raise serializers.ValidationError("Пользователь деактивирован")

        if not user.check_password(password):
            raise serializers.ValidationError("Неверный email или пароль")

        attrs["user"] = user
        return attrs


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "middle_name")
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
            "middle_name": {"required": False},
        }
