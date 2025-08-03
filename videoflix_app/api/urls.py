from django.urls import path, include
from django.http import FileResponse, Http404
from django.conf import settings
import os
from rest_framework.routers import DefaultRouter
from .views import  LogoutView, CustomUserView, CategoryViewSet, VideoViewSet, WatchHistoryViewSet, WatchlistViewSet, WatchlistEntryViewSet, serve_hls_manifest, serve_hls_segment
from .views import RegistrationView, ActivateUserView, CookieTokenObtainPairView, CookieTokenRefreshView, CheckLoginOrRegisterView, PasswordResetRequestView, PasswordResetConfirmView



router = DefaultRouter()
router.register(r'user', CustomUserView, basename='user')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'video', VideoViewSet, basename='video')
router.register(r'watchlist', WatchlistViewSet, basename='watchlist')
router.register(r'watchlist-entries', WatchlistEntryViewSet, basename='watchlist-entry')
router.register(r'history', WatchHistoryViewSet, basename='history')
    
urlpatterns = [   
    path('', include(router.urls)),
    path('register/', RegistrationView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', ActivateUserView.as_view(),name='activate-user'),      
    path('login/', CookieTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),   
    path('logout/', LogoutView.as_view(), name='logout'),
    path('users/check-login-register/', CheckLoginOrRegisterView.as_view(), name='check-login-register'), 
    path('password_reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password_confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_confirm'),   
    path('video/<int:movie_id>/<str:resolution>/index.m3u8', serve_hls_manifest, name='serve_hls_manifest'),
    path('video/<int:movie_id>/<str:resolution>/<str:segment>/', serve_hls_segment, name='serve_hls_segment'),   
    
]


