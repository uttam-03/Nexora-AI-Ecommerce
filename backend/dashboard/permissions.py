from rest_framework.permissions import BasePermission
class IsPlatformAdmin(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and (u.is_superuser or (u.is_staff and u.role == 'ADMIN')))
class IsActiveSeller(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.is_active and u.role == 'SELLER' and u.seller_approved)

class IsSellerAccount(BasePermission):
    def has_permission(self, request, view):
        u=request.user
        return bool(u and u.is_authenticated and u.is_active and u.role=='SELLER')
