import json
from rest_framework import serializers
from .models import Category, Product, ProductSpecification

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class ProductSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecification
        fields = ["id", "key", "value"]
        read_only_fields = ["id"]

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    sale_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    specifications = ProductSpecificationSerializer(many=True, required=False)
    image = serializers.ImageField(required=False, allow_null=True)
    image_url = serializers.URLField(required=False, allow_blank=True)
    class Meta:
        model = Product
        fields = ["id","brand","name","slug","description","price","discount_price","sale_price","stock","rating","review_count","image_url","image","category","category_name","is_featured","is_trending","created_at","specifications","is_active","seller"]
        read_only_fields = ["id", "rating", "review_count", "created_at", "seller"]

    def to_internal_value(self, data):
        if hasattr(data, "get") and isinstance(data.get("specifications"), str):
            data = data.copy()
            try: data["specifications"] = json.loads(data["specifications"] or "[]")
            except (TypeError, ValueError): raise serializers.ValidationError({"specifications": "Specifications must be valid JSON."})
        return super().to_internal_value(data)

    def _save_specs(self, product, specs):
        if specs is None:
            return
        product.specifications.all().delete()
        ProductSpecification.objects.bulk_create([
            ProductSpecification(product=product, key=item["key"].strip(), value=item["value"].strip())
            for item in specs if item.get("key", "").strip() and item.get("value", "").strip()
        ])

    def create(self, validated_data):
        specs = validated_data.pop("specifications", [])
        product = super().create(validated_data)
        self._save_specs(product, specs)
        return product

    def update(self, instance, validated_data):
        specs = validated_data.pop("specifications", None)
        product = super().update(instance, validated_data)
        self._save_specs(product, specs)
        return product
