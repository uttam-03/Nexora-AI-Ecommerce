from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (DashboardOverviewView, AdminUsersView, AdminUserActionView, AdminCreateAccountView, DashboardOrdersView, AdminProductViewSet,
    SellerProductViewSet, ReviewListCreateView, FeedbackCreateView, AdminFeedbackViewSet,
    SellerFeedbackView, SellerReviewView)
router=DefaultRouter()
router.register('admin/products',AdminProductViewSet,basename='admin-products')
router.register('seller/products',SellerProductViewSet,basename='seller-products')
router.register('admin/feedback',AdminFeedbackViewSet,basename='admin-feedback')
urlpatterns=[
    path('overview/',DashboardOverviewView.as_view()), path('orders/',DashboardOrdersView.as_view()),
    path('admin/users/create/',AdminCreateAccountView.as_view()),
    path('admin/users/',AdminUsersView.as_view()), path('admin/users/<int:pk>/',AdminUserActionView.as_view()),
    path('reviews/',ReviewListCreateView.as_view()), path('feedback/',FeedbackCreateView.as_view()),
    path('seller/feedback/',SellerFeedbackView.as_view()), path('seller/reviews/',SellerReviewView.as_view()),
    path('',include(router.urls)),
]
