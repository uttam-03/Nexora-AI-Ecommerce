from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    use_in_migrations = True
    def create_user(self, username, email, password=None, **extra_fields):
        if not email: raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password); user.save(using=self._db); return user
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True); extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True); extra_fields['role'] = 'ADMIN'
        if extra_fields.get('is_staff') is not True or extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_staff=True and is_superuser=True')
        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = [('CUSTOMER','Customer'),('SELLER','Seller'),('ADMIN','Admin')]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    address_line = models.CharField(max_length=250, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    seller_approved = models.BooleanField(default=False)
    objects = UserManager()
    def __str__(self): return self.username

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=50, default='Home')
    full_name = models.CharField(max_length=120); phone = models.CharField(max_length=20)
    line1 = models.CharField(max_length=200); line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100); state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20); country = models.CharField(max_length=80, default='India')
    is_default = models.BooleanField(default=False)
    class Meta: ordering = ['-is_default','-id']

class PaymentMethod(models.Model):
    TYPE_CHOICES = [('CARD','Card'),('UPI','UPI'),('COD','Cash on Delivery')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    method_type = models.CharField(max_length=10, choices=TYPE_CHOICES); provider = models.CharField(max_length=50, blank=True)
    display_name = models.CharField(max_length=100); last4 = models.CharField(max_length=4, blank=True)
    upi_id = models.CharField(max_length=120, blank=True); provider_customer_id = models.CharField(max_length=150, blank=True)
    is_default = models.BooleanField(default=False); created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.display_name
