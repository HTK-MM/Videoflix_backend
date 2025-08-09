# Admin

## class WatchlistAdmin (admin.ModelAdmin):

### def get_queryset(self, request):
Returns a QuerySet of Watchlist objects filtered by the user's permissions. If the current user is a superuser, returns all Watchlist objects. Otherwise, returns an empty QuerySet.   
    **Param Request:**
        - The current request object
    **Returns:**
        - A QuerySet of Watchlist objects
  
## class WatchlistEntryAdmin(admin.ModelAdmin):

### def get_user(self, obj):
Returns the user that the WatchlistEntry belongs to.
    **Param obj:**
        - The WatchlistEntry object
    **Returns:**
        - The user that the WatchlistEntry belongs to

### def get_queryset(self, request):
Returns a QuerySet of WatchlistEntry objects filtered by the user's permissions. If the current user is a superuser, returns all WatchlistEntry objects. Otherwise, returns an empty QuerySet.
    **Param Request:**
        - The current request object
    **Returns:**
        - A QuerySet of WatchlistEntry objects

## class WatchHistoryAdmin(admin.ModelAdmin):

### def get_queryset(self, request):
Returns a QuerySet of WatchHistory objects filtered by the user's permissions. If the current user is a superuser, returns all WatchHistory objects. Otherwise, returns an empty QuerySet.
    **Param Request:**
        - The current request object
    **Returns:**
        - A QuerySet of WatchHistory objects