# Permissions

## IsAdminOrReadOnly
This class, is a custom permission class in Django Rest Framework that controls access to views based on the request method and the user's staff status.

### def has_permission(self, request, view):
Check if the request has permission to proceed.
    For safe methods (e.g. GET, HEAD, OPTIONS), grant permission to all users.
    For other methods, grant permission only if the user is authenticated and is a staff member.
    **Args:**
        request: The HTTP request object.
        view: The view that is being accessed.
    **Returns:**
        bool: True if the request has permission, False otherwise.


## IsOwnerProfile
This class is a custom permission class in Django Rest Framework that checks if a user has ownership or permission to access a specific object.

### def has_permission(self, request, view):
    Return `True` if permission is granted, `False` otherwise.
    This method checks if the user is authenticated.

### def has_object_permission(self, request, view, obj):
CustomUser, Video, Watchlist and WatchlistEntry have an user attribute which is a foreign key to CustomUser.
    This method checks if the object's user matches the request's user.
    If the object doesn't have an user attribute, it will return False.
    If any Exception is thrown during the check, it will return False.