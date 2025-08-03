from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse, get_resolver
from django.contrib.auth import get_user_model
from videoflix_app.models import Video, Category
from videoflix_app.api.serializers import VideoSerializer, VideoListSerializer
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class VideoTests(APITestCase):

    def setUp(self):
        """ Setup the test data for video tests.
        This includes a user with admin permissions, a regular user, a category, and two videos.
        The videos are assigned to the category, and the admin user owns both videos.
        The second video is set as featured.
        The test client is also set up.       """
        
        self.admin_user = User.objects.create_user(username='admin',email='admin@example.com', password='adminpass', is_staff=True)
        self.regular_user = User.objects.create_user( username='testuser', email='test@example.com', password='testpass123')       
        self.category = Category.objects.create(name="TestCategory")
        temp_video = tempfile.NamedTemporaryFile(suffix='.mp4')
        temp_video.write(b"fake video content")
        temp_video.seek(0)

        self.video1 = Video.objects.create(
            title="Video 1",
            description="Desc 1",
            duration=100,
            video_file=SimpleUploadedFile(temp_video.name, temp_video.read(), content_type="video/mp4"),
            category=self.category,
            is_featured=True,
            user=self.admin_user
        )
        self.video2 = Video.objects.create(
            title="Video 2",
            description="Desc 2",
            duration=200,
            category=self.category,
            user=self.admin_user
        )
        self.client = APIClient()
        
        
    def test_list_videos(self):
        """ Tests that the list of videos is correctly returned to an authenticated user.
        The returned list should contain the videos' titles, descriptions, durations, thumbnail URLs, and categories.  """
        
        url = reverse('video-list')
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
        self.assertEqual(len(response.data), 2)
        self.assertIn('thumbnail_url', response.data[0])
        self.assertIn('category', response.data[0])


    def test_create_video_admin(self):
        """ Tests that an admin user can create a new video.
        The request should contain the title, description, duration, category ID, video file, and is_featured flag.
        The response should contain the message 'Video created successfully' and the newly created video should exist in the database. """
        
        url = reverse('video-list')
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'title': 'New Video',
            'description': 'Description',
            'duration': 120,
            'category_id': self.category.id,
            'video_file': SimpleUploadedFile("video.mp4", b"fake content", content_type="video/mp4"),
            'is_featured': False,
            'user': self.admin_user.id
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Video created successfully')
        self.assertTrue(Video.objects.filter(title='New Video').exists())


    def test_create_video_non_admin_forbidden(self):
        """ Tests that a non-admin user cannot create a new video.
        The request should contain the title, description, duration, category ID, video file, and is_featured flag.
        The response should have a 403 status code.  """
        
        url = reverse('video-list')
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'title': 'New Video',
            'description': 'Description',
            'duration': 120,
            'category_id': self.category.id,
            'is_featured': False,
            'user': self.regular_user.id
        }
        response = self.client.post(url, data, format='multipart')     
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_new_video_action(self):
        """ Tests that the new_video action is correctly implemented.
        The request should contain no data.
        The response should contain the title of the most recently created video.  """
        
        url = reverse('video-new-video')
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.video2.title) 


    def test_new_videos_action(self):
        """ Tests that the new_videos action is correctly implemented.
        The request should contain no data.
        The response should contain a list of the 10 most recently created videos.  """
        
        url = reverse('video-new-videos')
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)


    def test_featured_videos_action(self):
        """ Tests that the featured_videos action is correctly implemented.
        The request should contain no data.
        The response should contain a list of featured videos.  """
        
        url = reverse('video-featured')        
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)       
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.video1.title)