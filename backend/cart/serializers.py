from rest_framework import serializers
from .models import Cart, CartItem
from catalog.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source="product", read_only=True)
    line_total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    class Meta:
        model = CartItem
        fields = ["id","product","product_detail","quantity","line_total"]

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()
    def get_subtotal(self, obj): return sum((item.line_total for item in obj.items.select_related("product").all()), 0)
    def get_item_count(self, obj): return sum(item.quantity for item in obj.items.all())
    class Meta:
        model = Cart
        fields = ["id","items","subtotal","item_count","updated_at"]
