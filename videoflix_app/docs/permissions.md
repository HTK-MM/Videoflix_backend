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
Check if the request has permission to proceed. Grants permission to all authenticated users.
    **Args:**
        request (Request): The HTTP request object.
        view (View): The view that is being accessed.
    **Returns:**
        bool: True if the request has permission, False otherwise.

### def has_object_permission(self, request, view, obj):
Return `True` if permission is granted, `False` otherwise.
This method checks if the object is associated with the user making the request.
- If the object is a user, it checks if the object is the same as the user making the request.
- If the object has a `watchlist` attribute and the `watchlist` has a `user` attribute, it checks if the user associated with the `watchlist` is the same as the user making the request. 
- If the object has a `user` attribute, it checks if the user associated with the object is the same as the user making the request.
- If any Exception is thrown during the check, it will return False.
        **Param Request:**
            The request object
        **Param View:** 
            The view that is being accessed
        **Param obj:**
            The object that is being accessed
        **Returns:**
            bool: True if permission is granted, False otherwise. 
