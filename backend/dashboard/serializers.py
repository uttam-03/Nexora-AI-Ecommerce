from rest_framework import serializers
from .models import ProductReview, CustomerFeedback
from accounts.models import User
from catalog.models import Product
from catalog.serializers import ProductSerializer

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = ProductReview
        fields = ['id','user','username','product','product_name','rating','title','comment','is_visible','created_at']
        read_only_fields = ['id','user','is_visible','created_at']
    def validate_rating(self, value):
        if not 1 <= value <= 5: raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value

class FeedbackSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = CustomerFeedback
        fields = ['id','user','username','seller','product','product_name','feedback_type','subject','message','status','admin_response','created_at','updated_at']
        read_only_fields = ['id','user','status','admin_response','created_at','updated_at']

class UserAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','first_name','last_name','role','phone','is_active','seller_approved','date_joined','last_login']
        read_only_fields = ['id','username','email','role','date_joined','last_login']

class ProductManageSerializer(ProductSerializer):
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields
        read_only_fields = ['id','seller','rating','review_count','created_at']
