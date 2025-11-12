from django.contrib.auth import get_user_model
from rest_framework import serializers
from accounts.models import UserProfile

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ("id", "email", "password", "first_name", "last_name")
        read_only_fields = ("id",)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name")
        extra_kwargs = {
            "email": {"required": False},
            "first_name": {"required": False},
            "last_name": {"required": False},
            "password": {"required": False},
        }


class ProfileSerializer(serializers.ModelSerializer):
    user = UserNestedSerializer()

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "user",
            "phone",
            "date_of_birth",
        )
        read_only_fields = ("id",)

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        user = instance.user

        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
