from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Video, Category, Watchlist, WatchlistEntry, WatchHistory

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Video)
admin.site.register(Category)

@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['user']

    def get_queryset(self, request):
        """   Returns a QuerySet of Watchlist objects filtered by the user's permissions.    
        If the current user is a superuser, returns all Watchlist objects.
        Otherwise, returns an empty QuerySet.    
        :param request: The current request object
        :return: A QuerySet of Watchlist objects    """
        
        qs = super().get_queryset(request)
        return qs if request.user.is_superuser else qs.none()

@admin.register(WatchlistEntry)
class WatchlistEntryAdmin(admin.ModelAdmin):
    list_display = ['watchlist', 'video', 'get_user']

    def get_user(self, obj):
        """    Returns the user that the WatchlistEntry belongs to.
        :param obj: The WatchlistEntry object
        :return: The user that the WatchlistEntry belongs to """
        return obj.watchlist.user
    get_user.short_description = 'User' 
    
    
    def get_queryset(self, request):
        """   Returns a QuerySet of WatchlistEntry objects filtered by the user's permissions.
        If the current user is a superuser, returns all WatchlistEntry objects.
        Otherwise, returns an empty QuerySet.
        :param request: The current request object
        :return: A QuerySet of WatchlistEntry objects   """

        qs = super().get_queryset(request)
        return qs if request.user.is_superuser else qs.none()
    
@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'video', 'progress_seconds', 'updated_at']
    list_filter = ['user', 'video']
    search_fields = ['user__username', 'video__title']

    def get_queryset(self, request):
        """  Returns a QuerySet of WatchHistory objects filtered by the user's permissions.
        If the current user is a superuser, returns all WatchHistory objects.
        Otherwise, returns an empty QuerySet.        
        :param request: The current request object
        :return: A QuerySet of WatchHistory objects    """
        
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.none()
