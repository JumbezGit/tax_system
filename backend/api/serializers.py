from rest_framework import serializers
from .models import User, TaxpayerProfile, TaxType, TaxAccount, PaymentRequest
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    declaration = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'declaration', 'role']  # Role for admin creation, but default Taxpayer

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        if not data.get('declaration'):
            raise serializers.ValidationError("Declaration must be checked")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(email=validated_data['email'], password=validated_data['password'])
        return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxpayerProfile
        fields = '__all__'

# Add similar serializers for TaxAccount, PaymentRequest, etc.
class TaxAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxAccount
        fields = '__all__'

class PaymentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentRequest
        fields = '__all__'

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    role = serializers.CharField(required=False)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if user and user.is_active:
            if data.get('role') and data['role'] != user.role:
                raise serializers.ValidationError("Role mismatch")
            return user
        raise serializers.ValidationError("Incorrect credentials")

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role']