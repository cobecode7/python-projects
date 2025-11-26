
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, Address, UserProfile


class UserSerializer(serializers.ModelSerializer):
    """مسلسل بيانات المستخدم"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'birth_date', 'avatar', 'is_verified']
        read_only_fields = ['id', 'is_verified']


class RegisterSerializer(serializers.ModelSerializer):
    """مسلسل بيانات تسجيل المستخدم الجديد"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("كلمتا المرور غير متطابقتين")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """مسلسل بيانات تسجيل الدخول"""
    email = serializers.EmailField()
    password = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    """مسلسل بيانات تغيير كلمة المرور"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("كلمتا المرور غير متطابقتين")
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    """مسلسل بيانات طلب إعادة تعيين كلمة المرور"""
    email = serializers.EmailField()


class ConfirmResetPasswordSerializer(serializers.Serializer):
    """مسلسل بيانات تأكيد إعادة تعيين كلمة المرور"""
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("كلمتا المرور غير متطابقتين")
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """مسلسل بيانات ملف تعريف المستخدم"""
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'bio', 'website', 'location', 'facebook', 'twitter', 'instagram', 'linkedin', 
                  'email_notifications', 'push_notifications', 'sms_notifications']


class AddressSerializer(serializers.ModelSerializer):
    """مسلسل بيانات العناوين"""

    class Meta:
        model = Address
        fields = ['id', 'type', 'first_name', 'last_name', 'company', 'address_line_1', 'address_line_2',
                  'city', 'state', 'postal_code', 'country', 'phone', 'default']
        read_only_fields = ['id']

    def create(self, validated_data):
        # إذا كان هذا هو العنوان الأول أو تم تحديده كعنوان افتراضي
        if validated_data.get('default', False) or not Address.objects.filter(user=self.context['request'].user).exists():
            # إلغاء تحديد جميع العناوين الافتراضية الأخرى
            Address.objects.filter(user=self.context['request'].user, default=True).update(default=False)
            validated_data['default'] = True

        return Address.objects.create(user=self.context['request'].user, **validated_data)

    def update(self, instance, validated_data):
        # إذا تم تحديد العنوان الحالي كعنوان افتراضي
        if validated_data.get('default', False):
            # إلغاء تحديد جميع العناوين الافتراضية الأخرى
            Address.objects.filter(user=self.context['request'].user, default=True).update(default=False)

        return super().update(instance, validated_data)
