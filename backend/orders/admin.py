from django.contrib import admin
from .models import Order, OrderItem, Payment, PaymentConfiguration
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "user", "status", "payment_method", "payment_status", "total", "created_at")
    list_filter = ("status", "payment_method", "payment_status")
    search_fields = ("order_number", "user__username", "payment_reference")
    inlines = [OrderItemInline]
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "user", "method", "amount", "status", "utr", "created_at")
    list_filter = ("method", "status")
    search_fields = ("utr", "order__order_number", "user__username")
@admin.register(PaymentConfiguration)
class PaymentConfigurationAdmin(admin.ModelAdmin):
    def has_add_permission(self, request): return not PaymentConfiguration.objects.exists()
    def has_delete_permission(self, request, obj=None): return False
