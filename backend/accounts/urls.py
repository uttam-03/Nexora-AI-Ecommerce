from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import RegisterView, ProfileView, AddressListCreateView, AddressDetailView, PaymentMethodListCreateView, PaymentMethodDetailView

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", TokenObtainPairView.as_view()),
    path("profile/", ProfileView.as_view()),
    path("addresses/", AddressListCreateView.as_view()),
    path("addresses/<int:pk>/", AddressDetailView.as_view()),
    path("payment-methods/", PaymentMethodListCreateView.as_view()),
    path("payment-methods/<int:pk>/", PaymentMethodDetailView.as_view()),
]
