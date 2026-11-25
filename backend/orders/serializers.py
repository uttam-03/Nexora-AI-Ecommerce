from rest_framework import serializers
from .models import Order, OrderItem, Payment, PaymentConfiguration

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payment_status = serializers.CharField(read_only=True)
    class Meta:
        model = Order
        fields = ["id","order_number","status","payment_method","payment_status","payment_reference","total","created_at","updated_at","address","items"]

class PaymentConfigurationSerializer(serializers.ModelSerializer):
    qr_image_url = serializers.SerializerMethodField()
    class Meta:
        model = PaymentConfiguration
        fields = ["store_name","upi_id","qr_image","qr_image_url","upi_enabled","cod_enabled","updated_at"]
        read_only_fields = ["qr_image_url","updated_at"]
    def get_qr_image_url(self, obj):
        request = self.context.get("request")
        if not obj.qr_image: return ""
        url = obj.qr_image.url
        return request.build_absolute_uri(url) if request else url

class PaymentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source="order.order_number", read_only=True)
    customer = serializers.CharField(source="user.username", read_only=True)
    class Meta:
        model = Payment
        fields = ["id","order","order_number","customer","method","amount","status","utr","submitted_at","verified_at","admin_note","created_at"]
        read_only_fields = fields
