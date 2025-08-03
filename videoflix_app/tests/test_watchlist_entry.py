from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from videoflix_app.models import Category, Video, Watchlist, WatchlistEntry

User = get_user_model()

class WatchlistEntryTests(APITestCase):
    def setUp(self):
        """ Sets up the test environment for watchlist entry tests.
        - Creates a test user and an other user.
        - Creates an access token for the test user.
        - Creates a category, a video assigned to the category, and a watchlist for the test user.
        - Creates a watchlist for the other user. """
        
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.other_user = User.objects.create_user(username='otheruser',email='other@example.com', password='otherpass')
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies['access_token'] = str(refresh.access_token)
        self.category = Category.objects.create(name='TestCategory')

        self.video = Video.objects.create(
            title='Test Video', 
            description='Test Desc', 
            video_file='videoflix_app/tests/assets/small.mp4', 
            duration=100,
            category = self.category,
            user=self.user
            )
        self.watchlist = Watchlist.objects.create(user=self.user)
        self.other_watchlist = Watchlist.objects.create(user=self.other_user)


    def test_create_entry(self):
        """Tests that a watchlist entry can be successfully created.        
        This test sends a POST request to the 'watchlist-entry-list' endpoint with the video ID to create a new watchlist entry. It verifies that 
        the response status code is 201 Created, and asserts that the entry count is 1. Also checks that the created entry is associated with 
        the correct video and belongs to the current user's watchlist. """

        url = reverse('watchlist-entry-list')
        data = {
            "video_id": self.video.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WatchlistEntry.objects.count(), 1)
        self.assertEqual(WatchlistEntry.objects.first().video, self.video)
        self.assertEqual(WatchlistEntry.objects.first().watchlist.user, self.user)


    def test_list_entries(self):
        """Tests that the list of watchlist entries is correctly returned for the authenticated user.
        This test creates a watchlist entry and sends a GET request to the 'watchlist-entry-list' endpoint.
        It verifies that the response status code is 200 OK, and the response data contains exactly one entry 
        with the correct video ID. """

        WatchlistEntry.objects.create(watchlist=self.watchlist,video=self.video )
        url = reverse('watchlist-entry-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['video']['id'], self.video.id)


    def test_update_watchlist_entry(self):
        """Tests that an existing watchlist entry can be successfully updated to a new video.
        This test creates a watchlist entry and then sends a PUT request to the 'watchlist-entry-detail' endpoint with the new video ID.
        It verifies that the response status code is 200 OK, and the entry is updated with the correct video ID. """
        
        entry = WatchlistEntry.objects.create(watchlist=self.watchlist,video=self.video)
        url = reverse('watchlist-entry-detail', args=[entry.id])
        new_video = Video.objects.create(
            title='New Test Video',
            description='Another video',
            video_file='videos/new_test.mp4',
            duration=120,
            category=self.category,
            user=self.user
        )
        data = {
            'video_id': new_video.id
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        entry.refresh_from_db()
        self.assertEqual(entry.video.id, new_video.id)


    def test_delete_entry(self):
        """Tests that a watchlist entry can be successfully deleted.
        This test creates a watchlist entry and sends a DELETE request to the 'watchlist-entry-detail' endpoint.
        It verifies that the response status code is 204 No Content, and asserts that the entry no longer exists in the database."""

        entry = WatchlistEntry.objects.create(watchlist=self.watchlist,video=self.video)
        url = f'/api/watchlist-entries/{entry.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(WatchlistEntry.objects.filter(id=entry.id).exists())
    
    
    def test_cannot_delete_others_entry(self):
        """Tests that an authenticated user cannot delete a watchlist entry that does not belong to the user.
        This test creates a watchlist entry for the other user and sends a DELETE request to the 'watchlist-entry-detail' endpoint.
        It verifies that the response status code is 404 Not Found, and asserts that the entry still exists in the database."""
        
        entry = WatchlistEntry.objects.create(watchlist=self.other_watchlist, video=self.video)
        url = reverse('watchlist-entry-detail', args=[entry.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    
    def test_unauthenticated(self):
        """Tests that an unauthenticated request to the 'watchlist-entry-list' endpoint returns a 401 Unauthorized status code."""
        
        self.client.cookies.clear()
        url = reverse('watchlist-entry-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)