
from rest_framework import permissions
from videoflix_app.models import CustomUser

class IsAdminOrReadOnly(permissions.BasePermission):
      def has_permission(self, request, view):
        """   Check if the request has permission to proceed.
        For safe methods (e.g. GET, HEAD, OPTIONS), grant permission to all users.
        For other methods, grant permission only if the user is authenticated and is a staff member.
        Args:
            request (Request): The HTTP request object.
            view (View): The view that is being accessed.
        Returns:
            bool: True if the request has permission, False otherwise.  """
            
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsOwnerProfile(permissions.BasePermission):    
    def has_permission(self, request, view):
        """  Return `True` if permission is granted, `False` otherwise.
        This method checks if the user is authenticated. """
    
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """  CustomUser, Video, Watchlist and WatchlistEntry have an user attribute which is a foreign key to CustomUser.
        This method checks if the object's user matches the request's user.
        If the object doesn't have an user attribute, it will return False.
        If any Exception is thrown during the check, it will return False. """
        
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