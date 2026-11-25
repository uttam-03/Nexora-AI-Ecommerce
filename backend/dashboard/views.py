from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import serializers
from catalog.models import Product, Category
from orders.models import Order
from .models import ProductReview, CustomerFeedback
from .serializers import ReviewSerializer, FeedbackSerializer, UserAdminSerializer, ProductManageSerializer
from .permissions import IsPlatformAdmin, IsActiveSeller, IsSellerAccount

User = get_user_model()


class AdminCreateAccountView(APIView):
    permission_classes=[IsPlatformAdmin]
    def post(self,request):
        username=request.data.get('username','').strip(); email=request.data.get('email','').strip()
        password=request.data.get('password',''); role=request.data.get('role','CUSTOMER')
        if role not in ['CUSTOMER','SELLER']:
            return Response({'detail':'Only customer or seller accounts can be created here. Admins must be created with createsuperuser.'},status=400)
        if not username or not email or len(password)<8:
            return Response({'detail':'Username, email and password (minimum 8 characters) are required.'},status=400)
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            return Response({'detail':'Username or email already exists.'},status=400)
        user=User.objects.create_user(username=username,email=email,password=password,role=role,
            first_name=request.data.get('first_name',''),last_name=request.data.get('last_name',''))
        return Response(UserAdminSerializer(user).data,status=201)

class DashboardOrdersView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def get(self,request):
        qs=Order.objects.select_related('user').prefetch_related('items')
        if request.user.is_superuser or (request.user.is_staff and request.user.role=='ADMIN'):
            pass
        elif request.user.role=='SELLER':
            qs=qs.filter(items__product__seller=request.user).distinct()
        else: return Response({'detail':'Not allowed'},status=403)
        data=[]
        for order in qs.order_by('-created_at')[:200]:
            items=order.items.all()
            if request.user.role=='SELLER' and not request.user.is_superuser:
                items=items.filter(product__seller=request.user)
            data.append({'id':order.id,'customer':order.user.username,'status':order.status,'payment_method':order.payment_method,'payment_status':order.payment_status,'order_number':order.order_number,
                'total':str(sum((i.line_total for i in items),0)),'created_at':order.created_at,
                'items':[{'name':i.product_name,'quantity':i.quantity,'line_total':str(i.line_total)} for i in items]})
        return Response(data)

class DashboardOverviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        u = request.user
        if u.is_superuser or (u.is_staff and u.role == 'ADMIN'):
            return Response({'role':'ADMIN','stats':{
                'users':User.objects.filter(role='CUSTOMER').count(), 'sellers':User.objects.filter(role='SELLER').count(),
                'pending_sellers':User.objects.filter(role='SELLER',seller_approved=False,is_active=True).count(),
                'products':Product.objects.count(),'active_products':Product.objects.filter(is_active=True).count(),
                'orders':Order.objects.count(),'open_complaints':CustomerFeedback.objects.filter(status='OPEN').count(),
                'reviews':ProductReview.objects.count(),'revenue':Order.objects.exclude(status='CANCELLED').aggregate(v=Sum('total'))['v'] or 0,
            }})
        if u.role == 'SELLER':
            qs=Product.objects.filter(seller=u)
            order_items=Order.objects.filter(items__product__seller=u).distinct()
            return Response({'role':'SELLER','approved':u.seller_approved,'stats':{
                'products':qs.count(),'active_products':qs.filter(is_active=True).count(),'out_of_stock':qs.filter(stock=0).count(),
                'orders':order_items.count(),'reviews':ProductReview.objects.filter(product__seller=u).count(),
                'feedback':CustomerFeedback.objects.filter(seller=u).count(),
                'revenue':sum((item.line_total for order in order_items for item in order.items.filter(product__seller=u)),0),
            }})
        return Response({'role':'CUSTOMER'},status=403)

class AdminUsersView(generics.ListAPIView):
    serializer_class=UserAdminSerializer; permission_classes=[IsPlatformAdmin]
    queryset=User.objects.all().order_by('-date_joined')
    def get_queryset(self):
        qs=super().get_queryset(); role=self.request.query_params.get('role')
        return qs.filter(role=role) if role in ['CUSTOMER','SELLER','ADMIN'] else qs

class AdminUserActionView(APIView):
    permission_classes=[IsPlatformAdmin]
    def patch(self,request,pk):
        try: target=User.objects.get(pk=pk)
        except User.DoesNotExist: return Response({'detail':'User not found'},status=404)
        if target.is_superuser: return Response({'detail':'Superuser protection: this account cannot be blocked here.'},status=400)
        if 'is_active' in request.data:
            target.is_active=bool(request.data['is_active'])
            if target.role=='SELLER' and not target.is_active:
                target.seller_approved=False
                Product.objects.filter(seller=target).update(is_active=False)
        if 'seller_approved' in request.data and target.role=='SELLER': target.seller_approved=bool(request.data['seller_approved'])
        target.save(update_fields=['is_active','seller_approved'])
        return Response(UserAdminSerializer(target).data)
    def delete(self,request,pk):
        try: target=User.objects.get(pk=pk)
        except User.DoesNotExist: return Response({'detail':'User not found'},status=404)
        if target.is_superuser: return Response({'detail':'Superuser cannot be removed.'},status=400)
        target.is_active=False
        if target.role=='SELLER':
            target.seller_approved=False
            Product.objects.filter(seller=target).update(is_active=False)
        target.save(update_fields=['is_active','seller_approved'])
        return Response({'detail':'Account deactivated. Historical orders and records were retained.'})

class AdminProductViewSet(viewsets.ModelViewSet):
    queryset=Product.objects.select_related('category','seller').all().order_by('-created_at')
    serializer_class=ProductManageSerializer; permission_classes=[IsPlatformAdmin]
    def perform_destroy(self,instance):
        instance.is_active=False; instance.save(update_fields=['is_active'])

class SellerProductViewSet(viewsets.ModelViewSet):
    serializer_class=ProductManageSerializer; permission_classes=[IsSellerAccount]
    def get_permissions(self):
        permission=IsSellerAccount if self.request.method in permissions.SAFE_METHODS else IsActiveSeller
        return [permission()]
    def get_queryset(self): return Product.objects.filter(seller=self.request.user).select_related('category').order_by('-created_at')
    def perform_create(self,serializer): serializer.save(seller=self.request.user)
    def perform_destroy(self,instance):
        instance.is_active=False; instance.save(update_fields=['is_active'])

class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class=ReviewSerializer
    def get_permissions(self): return [permissions.IsAuthenticated()] if self.request.method=='POST' else [permissions.AllowAny()]
    def get_queryset(self):
        qs=ProductReview.objects.filter(is_visible=True).select_related('user','product')
        pid=self.request.query_params.get('product')
        return qs.filter(product_id=pid) if pid else qs
    def perform_create(self,serializer):
        product=Product.objects.get(pk=self.request.data.get('product'),is_active=True)
        review=serializer.save(user=self.request.user,product=product)
        aggregate=ProductReview.objects.filter(product=product,is_visible=True).aggregate(avg=Avg('rating'),count=Count('id'))
        product.rating=aggregate['avg'] or 0; product.review_count=aggregate['count']; product.save(update_fields=['rating','review_count'])

class FeedbackCreateView(generics.CreateAPIView):
    serializer_class=FeedbackSerializer; permission_classes=[permissions.IsAuthenticated]
    def perform_create(self,serializer):
        product=serializer.validated_data.get('product')
        seller=product.seller if product else None
        serializer.save(user=self.request.user,seller=seller)

class AdminFeedbackViewSet(viewsets.ModelViewSet):
    queryset=CustomerFeedback.objects.select_related('user','seller','product').all()
    serializer_class=FeedbackSerializer; permission_classes=[IsPlatformAdmin]
    def get_queryset(self):
        qs=super().get_queryset(); st=self.request.query_params.get('status')
        return qs.filter(status=st) if st else qs
    def partial_update(self,request,*args,**kwargs):
        instance=self.get_object()
        allowed={k:v for k,v in request.data.items() if k in ['status','admin_response','seller']}
        ser=self.get_serializer(instance,data=allowed,partial=True);ser.is_valid(raise_exception=True);ser.save();return Response(ser.data)

class SellerFeedbackView(generics.ListAPIView):
    serializer_class=FeedbackSerializer; permission_classes=[IsSellerAccount]
    def get_queryset(self): return CustomerFeedback.objects.filter(seller=self.request.user).select_related('user','product')

class SellerReviewView(generics.ListAPIView):
    serializer_class=ReviewSerializer; permission_classes=[IsSellerAccount]
    def get_queryset(self): return ProductReview.objects.filter(product__seller=self.request.user).select_related('user','product')
