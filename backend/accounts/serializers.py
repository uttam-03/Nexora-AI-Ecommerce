from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User, Address, PaymentMethod

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","username","email","first_name","last_name","role","phone","avatar","bio"]
        read_only_fields = ["id","username","role"]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model = User
        fields = ["id","username","email","password","first_name","last_name","role"]
        read_only_fields = ["id"]
    def validate_role(self, value):
        if value not in ["CUSTOMER", "SELLER"]:
            raise serializers.ValidationError("Only customer or seller registration is allowed.")
        return value
    def create(self, validated_data):
        password = validated_data.pop("password")
        role = validated_data.get("role", "CUSTOMER")
        if role == "ADMIN": raise serializers.ValidationError({"role": "Admin accounts can only be created with createsuperuser."})
        user = User.objects.create_user(password=password, **validated_data)
        return user

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"
        read_only_fields = ["user"]
    def validate(self, attrs):
        request = self.context.get("request")
        if attrs.get("is_default") and request and request.user.is_authenticated:
            # Default flag is changed only after serializer validation succeeds (save hook).
            attrs["_make_default"] = True
        return attrs
    def create(self, validated_data):
        make_default = validated_data.pop("_make_default", False)
        obj = super().create(validated_data)
        if make_default:
            Address.objects.filter(user=obj.user).exclude(pk=obj.pk).update(is_default=False)
        return obj
    def update(self, instance, validated_data):
        make_default = validated_data.pop("_make_default", False)
        obj = super().update(instance, validated_data)
        if make_default:
            Address.objects.filter(user=obj.user).exclude(pk=obj.pk).update(is_default=False)
        return obj

class PaymentMethodSerializer(serializers.ModelSerializer):
    # Never store full card number or CVV. Only token/last4 should be persisted.
    class Meta:
        model = PaymentMethod
        fields = ["id","method_type","provider","display_name","last4","upi_id","is_default","created_at"]
        read_only_fields = ["id","created_at"]
    def validate(self, attrs):
        if attrs.get("method_type") == "CARD" and len(attrs.get("last4", getattr(self.instance, "last4", ""))) not in (0,4):
            raise serializers.ValidationError({"last4":"Store exactly the last 4 digits only."})
        if attrs.get("is_default"):
            attrs["_make_default"] = True
        return attrs
    def create(self, validated_data):
        make_default = validated_data.pop("_make_default", False)
        obj = super().create(validated_data)
        if make_default:
            PaymentMethod.objects.filter(user=obj.user).exclude(pk=obj.pk).update(is_default=False)
        return obj
    def update(self, instance, validated_data):
        make_default = validated_data.pop("_make_default", False)
        obj = super().update(instance, validated_data)
        if make_default:
            PaymentMethod.objects.filter(user=obj.user).exclude(pk=obj.pk).update(is_default=False)
        return obj
