from django.conf import settings
from django.db import models
from catalog.models import Product

class ProductReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='product_reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='customer_reviews')
    rating = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=160, blank=True)
    comment = models.TextField()
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
        constraints = [models.UniqueConstraint(fields=['user','product'], name='one_review_per_user_product')]
    def __str__(self): return f'{self.product.name}: {self.rating}/5'

class CustomerFeedback(models.Model):
    TYPES = [('COMPLAINT','Complaint'),('FEEDBACK','Feedback'),('SERVICE','Service issue')]
    STATUS = [('OPEN','Open'),('IN_PROGRESS','In progress'),('RESOLVED','Resolved'),('CLOSED','Closed')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='submitted_feedback')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='seller_feedback')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedback')
    feedback_type = models.CharField(max_length=20, choices=TYPES, default='FEEDBACK')
    subject = models.CharField(max_length=180)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS, default='OPEN')
    admin_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering = ['-created_at']
    def __str__(self): return self.subject
