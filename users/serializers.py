from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    followers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    followers_count = SerializerMethodField()
    followed_count = SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'followed_users', 'followed_count', 'followers', 'followers_count', 'displayed_name', 'is_bot', 'bio']
        extra_kwargs = {
            'followed_users': {'read_only': True},
            'is_bot': {'read_only': True}
        }

    def get_followed_count(self, obj):
        return obj.followed_users.count()

    def get_followers_count(self, obj):
        return obj.followers.count()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords should be the same.'})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user