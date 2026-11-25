from django.contrib import admin
from .models import ProductReview, CustomerFeedback
@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display=('product','user','rating','is_visible','created_at');list_filter=('rating','is_visible');search_fields=('product__name','user__username','comment')
@admin.register(CustomerFeedback)
class CustomerFeedbackAdmin(admin.ModelAdmin):
    list_display=('subject','feedback_type','user','seller','status','created_at');list_filter=('feedback_type','status');search_fields=('subject','message','user__username')
