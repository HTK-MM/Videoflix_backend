from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from videoflix_app.models import  CustomUser, Category, Video, Watchlist, WatchlistEntry, WatchHistory
from django.contrib.auth import get_user_model, authenticate
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator

User = get_user_model()
token_generator = PasswordResetTokenGenerator()
        
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'address', 'phone']
        read_only_fields = ['username', 'email'] 
        
    def update(self, instance, validated_data):        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
        
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
  email = serializers.EmailField(write_only=True)
  password = serializers.CharField(write_only=True)
  
  class Meta:
        fields = ['email', 'password']

  def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)      
        self.fields.pop('username', None)  
  
  def validate(self, attrs):  
            email = attrs.get('email')         
            password = attrs.get('password')        
            user = CustomUser.objects.filter(email=email).first()
            if user is None:
                    raise serializers.ValidationError('Email address is not registered')                
            authenticated_user = authenticate(username=user.username, password=password)
            if not authenticated_user:
                    raise serializers.ValidationError('Invalid emailaddress or password')
            if not authenticated_user.is_active:
                    raise serializers.ValidationError('User is not active')            
            attrs['username'] = user.username            
            data = super().validate(attrs )
            data['user_id'] = user.id
            data['email'] = user.email          
            return data


class RegistrationSerializer(serializers.ModelSerializer):
    confirmed_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = [ 'email', 'password','confirmed_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters long.')
        return value
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value
    
    def validate(self, data):     
        if data['password'] != data['confirmed_password']:
            raise serializers.ValidationError({'password': 'Passwords must match'})
        return data
    
    def create(self, validated_data): 
        email = validated_data['email']
        password = validated_data['password']
        username = email.split('@')[0]        
        user = CustomUser.objects.create_user(username=username, email=email, password=password)
        return user

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    def validate_email(self, value):       
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):   
    new_password = serializers.CharField()
    repeat_password = serializers.CharField()

    def validate(self, data):        
        uidb64 = self.context.get('uidb64')
        token = self.context.get('token')
        if not uidb64 or not token:
            raise serializers.ValidationError("Missing uid or token")
        
        if data['new_password'] != data['repeat_password']:
            raise serializers.ValidationError("Passwords do not match")
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            raise serializers.ValidationError("Invalid UID")

        if not token_generator.check_token(user, token):
            raise serializers.ValidationError("Invalid or expired token")

        data['user'] = user
        return data

    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save()

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
    

class VideoSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    video_base_url = serializers.SerializerMethodField()  
    thumbnail_url = serializers.SerializerMethodField()   
    class Meta:
        model = Video
        fields =  ['id', 'title', 'description', 'duration', 'video_file', 'thumbnail','thumbnail_url', 'category','category_id', 'is_featured', 'created_at', 'user', 'video_base_url' ]
        read_only_fields = ['thumbnail']  
               
    def get_video_base_url(self, obj):        
        if obj.video_file:
            url = obj.video_file.url
            if url.endswith('.mp4'):
                return url.rsplit('.', 1)[0]
            return url
        return None    
    
    def get_thumbnail_url(self, obj):        
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None
class VideoListSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True)
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['id', 'created_at', 'title', 'description', 'thumbnail_url', 'category']
        read_only_fields = ['thumbnail']  
        
    def get_thumbnail_url(self, obj):        
        return VideoSerializer.get_thumbnail_url(self, obj)
 
class WatchlistEntrySerializer(serializers.ModelSerializer):
    video = VideoSerializer(read_only=True)
    video_id = serializers.PrimaryKeyRelatedField(queryset=Video.objects.all(), source='video', write_only=True)
    watchlist = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = WatchlistEntry
        fields = '__all__'
        
class WatchlistSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    entries = WatchlistEntrySerializer(source='watchlistentry_set', many=True, read_only=True)

    class Meta:
        model = Watchlist
        fields = '__all__'
        
class WatchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchHistory
        fields = ['id', 'user', 'video', 'watched_on', 'updated_at', 'progress_seconds']
        read_only_fields = ['watched_on', 'updated_at']        

        