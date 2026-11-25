from django.contrib import admin
from .models import Category, Product, ProductSpecification
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductSpecification)
