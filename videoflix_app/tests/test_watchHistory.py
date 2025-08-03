from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from videoflix_app.models import Category, Video, WatchHistory

User = get_user_model()

class WatchHistoryTests(APITestCase):
    def setUp(self):
        """ Setup the test environment for watch history tests.
        - Creates a test user and logs in to the client.
        - Creates an admin user.
        - Creates a category and a video assigned to the category.
        - Sets the video as featured, and assigns it to the test user.  """
        
        self.user = User.objects.create_user(username='test',email='test@example.com',  password='pass123')
        self.admin_user = User.objects.create_user(username='admin',email='admin@example.com', password='adminpass', is_staff=True)
        self.client.login(email='test@example.com',  password='pass123')  
        
        self.category = Category.objects.create(name="TestCategory")
        self.video = Video.objects.create(
            title='Test Video',
            description='Some description',
            video_file='videos/test.mp4',
            duration=600,
            is_featured=True,
            category_id=self.category.id,
            thumbnail='images/test.jpg',
            user=self.user
        )        
    

    def test_save_progress_creates_history(self):
        """Tests that posting to the save_progress endpoint creates a new WatchHistory object.
        - Logs in as the test user.
        - Posts a video_id and progress_seconds to the save_progress endpoint.
        - Asserts that the response code is 201 (created).
        - Asserts that there is one WatchHistory object created.
        - Asserts that the created WatchHistory object has the expected progress_seconds value.        """
        
        url = reverse('history-save-progress')
        data = {
            'video_id': self.video.id,
            'progress_seconds': 42
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WatchHistory.objects.count(), 1)
        self.assertEqual(WatchHistory.objects.first().progress_seconds, 42)


    def test_save_progress_updates_existing_history(self):
        """Tests that posting to the save_progress endpoint updates an existing WatchHistory object.
        - Logs in as the test user.
        - Creates a WatchHistory object with a progress_seconds value of 10.
        - Posts a video_id and progress_seconds to the save_progress endpoint.
        - Asserts that the response code is 200 (ok).
        - Asserts that there is one WatchHistory object created.
        - Asserts that the created WatchHistory object has the expected progress_seconds value of 90.        """
        
        WatchHistory.objects.create(user=self.user, video=self.video, progress_seconds=10)
        url = reverse('history-save-progress')
        data = {
            'video_id': self.video.id,
            'progress_seconds': 90
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(WatchHistory.objects.count(), 1)
        self.assertEqual(WatchHistory.objects.first().progress_seconds, 90)


    def test_get_progress_returns_existing_progress(self):
        """Tests that posting to the get_progress endpoint returns the existing progress value.
        - Creates a WatchHistory object with a progress_seconds value of 55.
        - Logs in as the test user.
        - Posts a video_id to the get_progress endpoint.
        - Asserts that the response code is 200 (ok).
        - Asserts that the response data contains a progress_seconds value of 55.        """
        
        WatchHistory.objects.create(user=self.user, video=self.video, progress_seconds=55)
        url = reverse('history-get-progress', kwargs={'video_id': self.video.id})
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['progress_seconds'], 55)


    def test_get_progress_returns_zero_if_not_exists(self):        
        """Tests that posting to the get_progress endpoint returns a progress value of 0 if there is no existing progress value.
        - Logs in as the test user.
        - Posts a video_id to the get_progress endpoint.
        - Asserts that the response code is 200 (ok).
        - Asserts that the response data contains a progress_seconds value of 0.        """
        
        url = reverse('history-get-progress', kwargs={'video_id': self.video.id})
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['progress_seconds'], 0)