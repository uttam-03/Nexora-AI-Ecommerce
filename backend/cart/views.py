from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from catalog.models import Product

class CartView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer
    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

class CartItemCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        try:
            quantity = int(request.data.get("quantity", 1))
        except (TypeError, ValueError):
            return Response({"detail": "Quantity must be a positive integer."}, status=400)
        if quantity < 1:
            return Response({"detail": "Quantity must be at least 1."}, status=400)
        product = get_object_or_404(Product, pk=request.data.get("product"), is_active=True)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        new_quantity = quantity if created else item.quantity + quantity
        if product.stock < new_quantity:
            if created: item.delete()
            return Response({"detail": f"Only {product.stock} unit(s) available."}, status=400)
        item.quantity = new_quantity
        item.save(update_fields=["quantity"])
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)

class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartItemSerializer
    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user).select_related("product")
    def update(self, request, *args, **kwargs):
        item = self.get_object()
        try: quantity = int(request.data.get("quantity", item.quantity))
        except (TypeError, ValueError): return Response({"detail":"Invalid quantity."}, status=400)
        if quantity < 1: return Response({"detail":"Quantity must be at least 1."}, status=400)
        if quantity > item.product.stock: return Response({"detail":f"Only {item.product.stock} unit(s) available."}, status=400)
        item.quantity = quantity; item.save(update_fields=["quantity"])
        return Response(CartItemSerializer(item).data)
