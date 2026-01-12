from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from xter import settings

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    followers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    followers_count = SerializerMethodField()
    followed_count = SerializerMethodField()
    profile_picture = SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'followed_users', 'followed_count', 'followers', 'followers_count', 'displayed_name', 'is_bot', 'bio', 'gender', 'profile_picture']
        extra_kwargs = {
            'followed_users': {'read_only': True},
            'is_bot': {'read_only': True}
        }

    def get_followed_count(self, obj):
        return obj.followed_users.count()

    def get_followers_count(self, obj):
        return obj.followers.count()
    
    def get_profile_picture(self, obj):
        request = self.context.get('request')

        if obj.profile_picture:
            try:
                url = obj.profile_picture.url

                if request:
                    return request.build_absolute_uri(url)
                return url

            except ValueError:
                pass

        default_url = settings.STATIC_URL + 'images/default_profile_picture.png'

        if request:
            return request.build_absolute_uri(default_url)
        return default_url

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'displayed_name', 'bio', 'gender', 'profile_picture']

    def validate_profile_picture(self, picture):
        if not picture:
            return picture
        
        allowed_ext = ('jpg', 'jpeg', 'png', 'webp')
        ext = picture.name.split('.')[-1].lower()

        if ext not in allowed_ext:
            raise serializers.ValidationError(f'.{ext} extension is not allowed.')
        
        if picture.size > 2 * 1024 * 1024:
            raise serializers.ValidationError('File is too large. Maximum size is 2MB.')

    def validate(self, attrs):
        if attrs['password2'] != attrs['password']:
            raise serializers.ValidationError({'password': 'Passwords should be the same.'})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user
    
class EditProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['displayed_name', 'bio', 'gender', 'profile_picture']
        extra_kwargs = {
            'displayed_name': {'required': False},
            'bio': {'required': False},
            'gender': {'required': False}
        }

    def validate_profile_picture(self, picture):
        if not picture:
            return picture
        
        allowed_ext = ('jpg', 'jpeg', 'png', 'webp')
        ext = picture.name.split('.')[-1].lower()

        if ext not in allowed_ext:
            raise serializers.ValidationError(f'.{ext} extension is not allowed.')
        
        if picture.size > 2 * 1024 * 1024:
            raise serializers.ValidationError('File is too large. Maximum size is 2MB.')
        
        return picture
        
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user

        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        
        return value

    def validate(self, attrs):
        if attrs['password2'] != attrs['password']:
            raise serializers.ValidationError({'password2': 'Passwords should be the same.'})
        
        if attrs['password'] == attrs['old_password']:
            raise serializers.ValidationError({'password': 'New password cannot be the same as the old password.'})

        return attrs
    
    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['password'])
        user.save()

        return user