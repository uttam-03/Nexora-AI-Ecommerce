from django.conf import settings
from django.db import models
from catalog.models import Product

class UserInteraction(models.Model):
    TYPES = [("VIEW","View"),("WISHLIST","Wishlist"),("CART","Cart"),("PURCHASE","Purchase"),("SEARCH","Search")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="interactions")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    interaction_type = models.CharField(max_length=20, choices=TYPES)
    query = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
