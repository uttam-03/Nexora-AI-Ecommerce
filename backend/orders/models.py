import uuid
from django.conf import settings
from django.db import models
from catalog.models import Product
from accounts.models import Address

class PaymentConfiguration(models.Model):
    store_name = models.CharField(max_length=120, default="Nexora AI")
    upi_id = models.CharField(max_length=120, blank=True)
    qr_image = models.ImageField(upload_to="payment_qr/", blank=True, null=True)
    upi_enabled = models.BooleanField(default=True)
    cod_enabled = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Payment configuration"
        verbose_name_plural = "Payment configuration"
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    @classmethod
    def current(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

class Order(models.Model):
    STATUS = [("PLACED","Placed"),("CONFIRMED","Confirmed"),("PROCESSING","Processing"),("SHIPPED","Shipped"),("OUT_FOR_DELIVERY","Out for delivery"),("DELIVERED","Delivered"),("CANCELLED","Cancelled"),("RETURNED","Returned")]
    PAYMENT = [("COD","Cash on Delivery"),("UPI","UPI QR")]
    PAYMENT_STATUS = [("PENDING","Pending"),("SUBMITTED","UTR submitted"),("PAID","Paid"),("REJECTED","Rejected"),("REFUNDED","Refunded")]
    order_number = models.CharField(max_length=24, unique=True, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    address = models.ForeignKey(Address, on_delete=models.PROTECT)
    status = models.CharField(max_length=30, choices=STATUS, default="PLACED")
    payment_method = models.CharField(max_length=20, choices=PAYMENT, default="COD")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="PENDING")
    payment_reference = models.CharField(max_length=150, blank=True)
    payment_verified_at = models.DateTimeField(null=True, blank=True)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = "NXR-" + uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    line_total = models.DecimalField(max_digits=14, decimal_places=2)

class Payment(models.Model):
    STATUS = [("PENDING","Pending"),("SUBMITTED","Submitted"),("VERIFIED","Verified"),("REJECTED","Rejected"),("COLLECTED","Collected")]
    order = models.OneToOneField(Order, on_delete=models.PROTECT, related_name="payment")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="payments")
    method = models.CharField(max_length=10, choices=[("UPI","UPI"),("COD","COD")])
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=12, choices=STATUS, default="PENDING")
    utr = models.CharField(max_length=80, blank=True, db_index=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="verified_nexora_payments")
    admin_note = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
