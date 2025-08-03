import os
from django.http import FileResponse, Http404
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.conf import settings
from django_rq import get_queue

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status,viewsets,permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes

from .tasks import send_activation_email_task, send_resetPW_email_task
from .authentication import CookieJWTAuthentication
from .serializers import CustomUserSerializer, MyTokenObtainPairSerializer, PasswordResetConfirmSerializer, PasswordResetRequestSerializer, RegistrationSerializer
from .serializers import  CategorySerializer, VideoSerializer, VideoListSerializer, WatchHistorySerializer, WatchlistSerializer, WatchlistEntrySerializer
from videoflix_app.models import CustomUser, Category, Video, WatchHistory, Watchlist, WatchlistEntry    
from .permissions import IsAdminOrReadOnly, IsOwnerProfile
import traceback

User = get_user_model()

class CustomUserView(viewsets.ModelViewSet):    
    serializer_class = CustomUserSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerProfile]
    
    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)
    def get_object(self):
        return self.request.user
    def destroy(self, request, *args, **kwargs):
        return Response({'detail': 'Deleting account is not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    @action(detail=False, methods=['get', 'put', 'patch'], url_path='me')
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        elif request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = self.get_serializer(user, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

class RegistrationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = default_token_generator.make_token(user)
            queue = get_queue('default')
            queue.enqueue(send_activation_email_task, user.id)
            
            return Response({"user": {
                    "id": user.id,
                    "email": user.email
                },
                "token": token}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

class ActivateUserView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, uidb64=None, token=None):
        print(f"ActivateUserView GET called with uidb64={uidb64} and token={token}")
        if not uidb64 or not token:
            return Response({'error': 'UID and token are required'}, status=status.HTTP_400_BAD_REQUEST)
        return self.activate_user(uidb64, token)    
    
    def post(self, request, uidb64=None, token=None ):
        uidb64 = request.data.get('uid') or uidb64
        token = request.data.get('token') or token     
        if not uidb64 or not token:
            return Response({'error': 'UID and token are required'}, status=status.HTTP_400_BAD_REQUEST)
        return self.activate_user(uidb64, token)
    
    def activate_user(self, uidb64, token):        
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid UID'}, status=status.HTTP_400_BAD_REQUEST)
        
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'message': 'Account successfully activated.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        

    
class CookieTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = MyTokenObtainPairSerializer      
    def post(self, request, *args, **kwargs):       
        response = super().post(request, *args, **kwargs)
        refresh = response.data.get("refresh")
        access = response.data.get("access")
        
        is_secure = not settings.DEBUG 
        response.set_cookie( 
            key="access_token", 
            value = access,
            httponly=True,
            samesite="Lax",            
            secure=is_secure,      
            )
        
        response.set_cookie(
            key="refresh_token",
            value = refresh,
            httponly=True,
            samesite="Lax",             
            secure=is_secure,                
            )
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        response.data = {"detail": "Login successful", "user": { "id": user.id, "username": user.email }}
        return response
    
class CookieTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")        
        if refresh_token is None:
            return Response({"error": "Refresh token not found in cookies"}, status=status.HTTP_400_BAD_REQUEST)        
        serializer = self.get_serializer(data={"refresh": refresh_token})        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"detail": "Refresh token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)        
        access_token = serializer.validated_data.get("access")
        response = Response({"message": "access Token refreshed successfully"}, status=status.HTTP_200_OK)        
        is_secure = not settings.DEBUG 
        response.set_cookie( 
            key="access_token", 
            value = access_token,
            httponly=True,
            secure=is_secure,
            samesite="Lax"
        )
        return response

class LogoutView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response(
                {"error": "Refresh token is missing."}, status=status.HTTP_400_BAD_REQUEST )
        try:           
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"error": "Invalid or expired refresh token."}, status=status.HTTP_400_BAD_REQUEST )
        response = Response(
            { "detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid." },
            status=status.HTTP_200_OK )
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response

class CheckLoginOrRegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'detail': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        exists = User.objects.filter(email=email).exists()
        return Response({
            'shouldLogin': exists,
            'shouldRegister': not exists
        }, status=status.HTTP_200_OK)

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = User.objects.filter(email=serializer.validated_data['email']).first()
            if user:
                queue = get_queue('default')
                queue.enqueue(send_resetPW_email_task, user.id)

            return Response(
                {'detail': 'An email has been sent to reset your password.'},
                status=status.HTTP_200_OK )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
            
class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, uidb64, token):
        serializer = self.serializer_class(data=request.data,context={'uidb64': uidb64, 'token': token})          
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Your Password has been successfully reset."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
  
  
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"error": "Only admins can create categories."}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            return Response({"message":"Category created successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)     
  
    @action(detail=False, methods=['get'], url_path='with_videos')
    def categories_with_videos(self, request):
        categories = self.get_queryset()
        data = []
        for category in categories:
            videos = Video.objects.filter(category=category)
            videos_serializer = VideoSerializer(videos, many=True)
            data.append({
                'category': category.name,
               'videos': videos_serializer.data
            })
        return Response(data)
  
class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return VideoListSerializer
        return VideoSerializer

    def create(self, request, *args, **kwargs):        
        serializer = self.get_serializer(data=request.data)        
        if serializer.is_valid(raise_exception = True):
            serializer.save()                   
            return Response({"message":"Video created successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='new')
    def new_video(self, request):
        video =self.get_queryset().order_by('-created_at').first()         
        serializer = self.get_serializer(video)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='new_videos')
    def new_videos(self, request):
        videos = self.get_queryset().order_by('-created_at')[:10]        
        serializer = self.get_serializer(videos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='featured')
    def featured(self, request):
        videos = self.get_queryset().filter(is_featured=True)        
        serializer = self.get_serializer(videos, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieJWTAuthentication])
def serve_hls_manifest(request, movie_id, resolution):
    file_path = os.path.join(settings.MEDIA_ROOT, 'videos', str(movie_id), resolution, 'index.m3u8')
    if not os.path.exists(file_path):
        raise Http404("Video or Manifest file not found")
    return FileResponse(open(file_path, 'rb'), content_type='application/vnd.apple.mpegurl')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieJWTAuthentication])
def serve_hls_segment(request, movie_id, resolution, segment):
    file_path = os.path.join(settings.MEDIA_ROOT,'videos', str(movie_id), resolution, segment)
    if not os.path.exists(file_path):
        raise Http404("Video or Segment file not found")
    return FileResponse(open(file_path, 'rb'), content_type='video/MP2T')

    
class WatchlistViewSet(viewsets.ModelViewSet):
    serializer_class = WatchlistSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerProfile]

    def get_queryset(self):     
        return Watchlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class WatchlistEntryViewSet(viewsets.ModelViewSet):
    serializer_class = WatchlistEntrySerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerProfile]

    def get_queryset(self):       
        return WatchlistEntry.objects.filter(watchlist__user=self.request.user)

    def perform_create(self, serializer):   
        watchlist, _ = Watchlist.objects.get_or_create(user=self.request.user)    
        video = serializer.validated_data.get('video')
        if WatchlistEntry.objects.filter(watchlist=watchlist, video=video).exists():
            raise serializer.ValidationError("This video is already in your watchlist.")
        serializer.save(watchlist=watchlist)
        
    @action(detail=False, methods=['delete'], url_path='remove/(?P<video_id>[^/.]+)')
    def remove_video(self, request, video_id=None):
        watchlist = Watchlist.objects.filter(user=request.user).first()
        if not watchlist:
            return Response({"error": "Watchlist not found"}, status=status.HTTP_404_NOT_FOUND)

        entry = WatchlistEntry.objects.filter(watchlist=watchlist, video_id=video_id).first()
        if not entry:
            return Response({"error": "Video not in watchlist"}, status=status.HTTP_404_NOT_FOUND)

        entry.delete()
        return Response({"message": "Video removed from watchlist"}, status=status.HTTP_204_NO_CONTENT)

class WatchHistoryViewSet(viewsets.ModelViewSet):    
    serializer_class = WatchHistorySerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerProfile]

    def get_queryset(self):       
        return WatchHistory.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'],url_path='save-progress')
    def save_progress(self, request):
        video_id = request.data.get('video_id')
        seconds = request.data.get('progress_seconds')
        if not video_id or seconds is None:
            return Response({"error": "Missing video_id or progress_seconds"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            seconds = int(seconds)
            video = Video.objects.filter(id=video_id).first()
        except (ValueError, video.DoesNotExist):
            return Response({"error": "Invalid input or video not found"}, status=status.HTTP_400_BAD_REQUEST)       
        history, created = WatchHistory.objects.update_or_create( user=request.user, video=video, defaults={'progress_seconds': seconds} )
        serializer = self.get_serializer(history)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='get-progress/(?P<video_id>[^/.]+)')
    def get_progress(self, request, video_id=None):
        history = WatchHistory.objects.filter(user=request.user, video_id=video_id).first()
        if not history:
            return Response({"progress_seconds": 0}) 
        serializer = self.get_serializer(history)
        return Response(serializer.data)