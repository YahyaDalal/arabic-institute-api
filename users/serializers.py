import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from config.sanitization import sanitize_string, sanitize_email

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2', 'role')

    def validate_email(self, value):
        return sanitize_email(value)

    def validate_username(self, value):
        sanitized = sanitize_string(value)
        if len(sanitized) < 3:
            raise serializers.ValidationError('Username must be at least 3 characters.')
        if not re.match(r'^[a-zA-Z0-9_]+$', sanitized):
            raise serializers.ValidationError('Username can only contain letters, numbers, and underscores.')
        return sanitized

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'role', 'bio', 'avatar', 'avatar_url')
        read_only_fields = ('email', 'role')

    def get_avatar_url(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None