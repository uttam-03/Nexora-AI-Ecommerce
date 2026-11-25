from django.urls import path
from .views import (OrderListCreateView, OrderDetailView, PaymentConfigurationView, UTRSubmitView,
    PaymentHistoryView, AdminPaymentListView, AdminPaymentActionView, AdminOrderStatusView, OrderInvoiceView)
urlpatterns = [
    path("", OrderListCreateView.as_view()),
    path("<int:order_id>/invoice/", OrderInvoiceView.as_view()),
    path("<int:pk>/", OrderDetailView.as_view()),
    path("payments/config/", PaymentConfigurationView.as_view()),
    path("payments/history/", PaymentHistoryView.as_view()),
    path("payments/submit-utr/<int:order_id>/", UTRSubmitView.as_view()),
    path("admin/payments/", AdminPaymentListView.as_view()),
    path("admin/payments/<int:payment_id>/action/", AdminPaymentActionView.as_view()),
    path("admin/<int:order_id>/status/", AdminOrderStatusView.as_view()),
]
