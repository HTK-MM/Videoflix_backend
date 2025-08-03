
from rest_framework import permissions
from videoflix_app.models import CustomUser

class IsAdminOrReadOnly(permissions.BasePermission):
      def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsOwnerProfile(permissions.BasePermission):    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    def has_object_permission(self, request, view, obj):
        try:
            if isinstance(obj, CustomUser):
                return obj == request.user
            if hasattr(obj, 'watchlist') and hasattr(obj.watchlist, 'user'):
                return obj.watchlist.user == request.user
            if hasattr(obj, 'user'):
                return obj.user == request.user
        except Exception as e:
            return False
        return False