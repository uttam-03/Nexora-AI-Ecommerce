from decimal import Decimal
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order, OrderItem, Payment, PaymentConfiguration
from .serializers import OrderSerializer, PaymentSerializer, PaymentConfigurationSerializer
from cart.models import Cart
from accounts.models import Address
from catalog.models import Product

class OrderListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer
    def get_queryset(self): return Order.objects.filter(user=self.request.user).prefetch_related("items")
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        config = PaymentConfiguration.current()
        method = str(request.data.get("payment_method", "COD")).upper()
        if method not in ("COD", "UPI"):
            return Response({"detail":"Choose UPI or Cash on Delivery."}, status=400)
        if method == "UPI" and not config.upi_enabled: return Response({"detail":"UPI payments are currently disabled."}, status=400)
        if method == "UPI" and (not config.upi_id or not config.qr_image): return Response({"detail":"UPI is not configured yet. Store admin must add the merchant UPI ID and QR code."}, status=400)
        if method == "COD" and not config.cod_enabled: return Response({"detail":"Cash on Delivery is currently disabled."}, status=400)
        cart = Cart.objects.filter(user=request.user).first()
        if not cart: return Response({"detail":"Your cart is empty."}, status=400)
        items = list(cart.items.select_related("product").select_for_update())
        if not items: return Response({"detail":"Your cart is empty."}, status=400)
        address = Address.objects.filter(id=request.data.get("address"), user=request.user).first()
        if not address: return Response({"detail":"Valid delivery address is required."}, status=400)
        locked_products = {}
        for item in items:
            product = Product.objects.select_for_update().get(pk=item.product_id)
            if not product.is_active or product.stock < item.quantity:
                return Response({"detail":f"{product.name} is unavailable in the requested quantity. Refresh your cart."}, status=400)
            locked_products[product.pk] = product
        order = Order.objects.create(user=request.user, address=address, payment_method=method,
            status="CONFIRMED" if method == "COD" else "PLACED",
            payment_status="PENDING")
        total = Decimal("0.00")
        for item in items:
            product = locked_products[item.product_id]
            price = product.sale_price
            line = price * item.quantity
            OrderItem.objects.create(order=order, product=product, product_name=product.name, unit_price=price, quantity=item.quantity, line_total=line)
            product.stock -= item.quantity
            product.save(update_fields=["stock"])
            total += line
        order.total = total
        order.save(update_fields=["total"])
        Payment.objects.create(order=order, user=request.user, method=method, amount=total, status="PENDING")
        cart.items.all().delete()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer
    def get_queryset(self): return Order.objects.filter(user=self.request.user).prefetch_related("items")

class OrderInvoiceView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, order_id):
        order = get_object_or_404(Order.objects.prefetch_related("items").select_related("address"), pk=order_id, user=request.user)
        a = order.address
        return Response({"order_number":order.order_number,"created_at":order.created_at,"status":order.status,
            "payment_method":order.payment_method,"payment_status":order.payment_status,"total":str(order.total),
            "customer":order.user.get_full_name() or order.user.username,"email":order.user.email,
            "address":{"full_name":a.full_name,"phone":a.phone,"line1":a.line1,"line2":a.line2,"city":a.city,"state":a.state,"postal_code":a.postal_code,"country":a.country},
            "items":[{"name":i.product_name,"unit_price":str(i.unit_price),"quantity":i.quantity,"line_total":str(i.line_total)} for i in order.items.all()]})

class PaymentConfigurationView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        obj = PaymentConfiguration.current()
        data = PaymentConfigurationSerializer(obj, context={"request":request}).data
        # Only expose the merchant details needed for checkout.
        return Response({k:data[k] for k in ["store_name","upi_id","qr_image_url","upi_enabled","cod_enabled"]})
    def patch(self, request):
        if not request.user.is_authenticated or not (request.user.is_superuser or (request.user.is_staff and request.user.role == "ADMIN")):
            return Response({"detail":"Admin access required."}, status=403)
        obj = PaymentConfiguration.current()
        serializer = PaymentConfigurationSerializer(obj, data=request.data, partial=True, context={"request":request})
        serializer.is_valid(raise_exception=True); serializer.save()
        return Response(serializer.data)

class UTRSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    @transaction.atomic
    def post(self, request, order_id):
        order = get_object_or_404(Order.objects.select_for_update(), pk=order_id, user=request.user, payment_method="UPI")
        if order.payment_status == "PAID": return Response({"detail":"This order is already marked paid."}, status=400)
        utr = str(request.data.get("utr", "")).strip()
        if not (8 <= len(utr) <= 80) or not utr.isalnum():
            return Response({"detail":"Enter a valid transaction reference (8–80 letters/numbers)."}, status=400)
        if Payment.objects.filter(utr__iexact=utr).exclude(order=order).exists():
            return Response({"detail":"This transaction reference has already been submitted."}, status=400)
        payment = order.payment
        if payment.status == "VERIFIED": return Response({"detail":"Payment is already verified."}, status=400)
        payment.utr = utr; payment.status = "SUBMITTED"; payment.submitted_at = timezone.now(); payment.save(update_fields=["utr","status","submitted_at"])
        order.payment_reference = utr; order.payment_status = "SUBMITTED"; order.save(update_fields=["payment_reference","payment_status","updated_at"])
        return Response({"detail":"Transaction reference submitted. Order will be confirmed after admin verifies the merchant bank credit.","payment":PaymentSerializer(payment).data})

class PaymentHistoryView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentSerializer
    def get_queryset(self): return Payment.objects.filter(user=self.request.user).select_related("order").order_by("-created_at")

class AdminPaymentListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentSerializer
    def get_queryset(self):
        u=self.request.user
        if not (u.is_superuser or (u.is_staff and u.role == "ADMIN")): return Payment.objects.none()
        return Payment.objects.select_related("order","user","verified_by").order_by("-created_at")

class AdminPaymentActionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    @transaction.atomic
    def post(self, request, payment_id):
        u=request.user
        if not (u.is_superuser or (u.is_staff and u.role == "ADMIN")): return Response({"detail":"Admin access required."}, status=403)
        payment=get_object_or_404(Payment.objects.select_for_update().select_related("order"), pk=payment_id)
        action=str(request.data.get("action", "")).lower()
        note=str(request.data.get("note", ""))[:250]
        if action == "verify":
            if payment.method != "UPI" or payment.status != "SUBMITTED": return Response({"detail":"Only submitted UPI payments can be verified."}, status=400)
            payment.status="VERIFIED"; payment.verified_at=timezone.now(); payment.verified_by=u; payment.admin_note=note
            payment.order.payment_status="PAID"; payment.order.status="CONFIRMED"; payment.order.payment_verified_at=timezone.now()
            payment.order.save(update_fields=["payment_status","status","payment_verified_at","updated_at"])
        elif action == "reject":
            if payment.status != "SUBMITTED": return Response({"detail":"Only submitted payments can be rejected."}, status=400)
            payment.status="REJECTED"; payment.admin_note=note
            payment.order.payment_status="REJECTED"; payment.order.status="PLACED"
            payment.order.save(update_fields=["payment_status","status","updated_at"])
        elif action == "collect_cod":
            if payment.method != "COD" or payment.order.status != "DELIVERED": return Response({"detail":"COD can be collected only after delivery."}, status=400)
            payment.status="COLLECTED"; payment.verified_at=timezone.now(); payment.verified_by=u; payment.admin_note=note
            payment.order.payment_status="PAID"; payment.order.payment_verified_at=timezone.now()
            payment.order.save(update_fields=["payment_status","payment_verified_at","updated_at"])
        else: return Response({"detail":"Unknown payment action."}, status=400)
        payment.save()
        return Response(PaymentSerializer(payment).data)

class AdminOrderStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    @transaction.atomic
    def patch(self, request, order_id):
        u=request.user
        if not (u.is_superuser or (u.is_staff and u.role == "ADMIN")): return Response({"detail":"Admin access required."}, status=403)
        order=get_object_or_404(Order, pk=order_id)
        new_status=str(request.data.get("status", "")).upper()
        if new_status not in dict(Order.STATUS): return Response({"detail":"Invalid order status."}, status=400)
        if order.status == "CANCELLED" and new_status != "CANCELLED": return Response({"detail":"Cancelled orders cannot be reopened."}, status=400)
        if new_status == "CANCELLED" and order.status != "CANCELLED":
            if order.payment_status == "PAID":
                return Response({"detail":"This order has already been paid. Complete the refund process before cancelling it."}, status=400)
            for line in order.items.select_related("product").all():
                product = Product.objects.select_for_update().get(pk=line.product_id)
                product.stock += line.quantity
                product.save(update_fields=["stock"])
            if hasattr(order, "payment") and order.payment.status not in ("VERIFIED", "COLLECTED"):
                order.payment.status = "REJECTED"
                order.payment.admin_note = "Order cancelled by admin"
                order.payment.save(update_fields=["status", "admin_note"])
        order.status=new_status; order.save(update_fields=["status","updated_at"])
        return Response(OrderSerializer(order).data)
