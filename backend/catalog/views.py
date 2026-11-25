from rest_framework import viewsets, permissions
from django.db import models
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True, stock__gte=0).filter(models.Q(seller__isnull=True) | models.Q(seller__is_active=True, seller__seller_approved=True)).select_related("category", "seller").prefetch_related("specifications")
    serializer_class = ProductSerializer
    lookup_field = "slug"
    lookup_value_regex = r"[-a-zA-Z0-9_]+"
    search_fields = ["name","brand","description","category__name"]
    ordering_fields = ["price","rating","created_at","review_count"]
    ordering = ["-created_at"]

    @action(detail=False, methods=["get"])
    def trending(self, request):
        qs = self.get_queryset().filter(is_trending=True).order_by("-rating","-review_count")[:12]
        return Response(ProductSerializer(qs, many=True).data)

    @action(detail=False, methods=["get"])
    def featured(self, request):
        qs = self.get_queryset().filter(is_featured=True).order_by("-created_at")[:12]
        return Response(ProductSerializer(qs, many=True).data)

    @action(detail=False, methods=["get"])
    def deals(self, request):
        qs = self.get_queryset().exclude(discount_price=None).order_by("discount_price")[:12]
        return Response(ProductSerializer(qs, many=True).data)

    @action(detail=False, methods=["get"])
    def new_arrivals(self, request):
        qs = self.get_queryset().order_by("-created_at")[:12]
        return Response(ProductSerializer(qs, many=True).data)
