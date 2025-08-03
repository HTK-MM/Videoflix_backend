from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):    
    custom = models.CharField(max_length=500, null=True, blank=True)
    address = models.CharField(max_length=150, null=True, blank=True)
    phone = models.CharField(max_length=25, null=True, blank=True)

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Video(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    thumbnail = models.ImageField(upload_to='images/', null=True, blank=True)
    video_file = models.FileField(upload_to='videos/', null=True, blank=True) 
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)   
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title  

class WatchHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    watched_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    progress_seconds = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('user', 'video')

    def __str__(self):
        return f"{self.user.username} watched {self.video.title}"

class Watchlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    movies = models.ManyToManyField(Video, through='WatchlistEntry')

class WatchlistEntry(models.Model):
    watchlist = models.ForeignKey(Watchlist, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)