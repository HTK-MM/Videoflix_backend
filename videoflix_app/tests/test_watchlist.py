from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from videoflix_app.models import Category, Video, WatchlistEntry, Watchlist

User = get_user_model()

class WatchlistTests(APITestCase):
    def setUp(self):
        """Setup the test environment for watchlist tests.
        - Creates a test user and an other user.
        - Creates an access token for the test user.
        - Creates a category, a video assigned to the category, and a watchlist for the test user.
        - Creates a watchlist for the other user. """

        self.user = User.objects.create_user(username='user1', email='test@example.com',  password='pass123')
        self.other_user = User.objects.create_user(username='user2', email='other@example.com', password='pass456')
        self.category = Category.objects.create(name='TestCategory')
        self.client.force_authenticate(user=self.user)
        self.video = Video.objects.create(
            title='Test Video',
            description='A test video',
            video_file='videos/test.mp4',
            duration=100,
            category = self.category,
            user=self.user
        )
        self.watchlist = Watchlist.objects.create(user=self.user)        
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies['access_token'] = str(refresh.access_token)
   
   
    def test_get_user_watchlist(self):
        """Tests that a GET request to the watchlist endpoint returns the watchlist for the currently authenticated user."""
        url = reverse('watchlist-list')  
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user'], self.user.username)      
        
          
    def test_add_watchlist_entry(self):
        """Tests that a POST request to the watchlist-entry endpoint with a video id successfully creates a watchlist entry for the authenticated user."""
        
        url = reverse('watchlist-entry-list') 
        data = {
            'video_id': self.video.id,
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WatchlistEntry.objects.count(), 1)
        self.assertEqual(WatchlistEntry.objects.first().watchlist.user, self.user)


    def test_unauthenticated_access(self):
        """Tests that an unauthenticated request to the watchlist endpoint returns a 401 Unauthorized status code."""
        
        self.client.logout()
        url = reverse('watchlist-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_user_cannot_access_others_watchlist(self):       
        """Tests that an authenticated user cannot access another user's watchlist by sending a GET request to the watchlist endpoint.
        - Creates a watchlist for the other user.
        - Sends a GET request to the watchlist endpoint.
        - Asserts that the response contains only the authenticated user's watchlist."""
        
        Watchlist.objects.create(user=self.other_user)
        url = reverse('watchlist-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user'], self.user.username)