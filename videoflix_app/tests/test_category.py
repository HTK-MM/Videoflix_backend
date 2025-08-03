from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from videoflix_app.models import Category, Video
from videoflix_app.api.serializers import VideoSerializer

User = get_user_model()

class CategoryTests(APITestCase):

    def setUp(self):     
        """     Setup the test data for category tests.
        This includes a user with admin permissions, a regular user, three categories, and three videos.
        The videos are assigned to the categories.    """
        
        self.admin_user = User.objects.create_user(username='admin',email='admin@example.com', password='adminpass', is_staff=True)
        self.regular_user = User.objects.create_user( username='testuser', email='test@example.com', password='testpass123')
        self.client = APIClient()

        self.category1 = Category.objects.create(name="Category 1")
        self.category2 = Category.objects.create(name="Category 2")

        self.video1 = Video.objects.create(title="Video 1", category=self.category1, duration=120, user = self.admin_user)
        self.video2 = Video.objects.create(title="Video 2", category=self.category1, duration=80, user=self.admin_user)
        self.video3 = Video.objects.create(title="Video 3", category=self.category2, duration=140, user=self.admin_user)


    def test_list_categories(self):       
        """ Test that the list of categories is correctly returned to an unauthenticated user """
        
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


    def test_create_category_admin(self):       
        """Test that an admin user can create a new category"""
        
        url = reverse('category-list')
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'New Category'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Category created successfully')
        self.assertTrue(Category.objects.filter(name='New Category').exists())


    def test_create_category_non_admin(self):
        """Test that a non-admin user cannot create a new category"""
        
        url = reverse('category-list')
        self.client.force_authenticate(user=self.regular_user)
        data = {'name': 'New Category'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have permission to perform this action.')


    def test_categories_with_videos_action(self):
        """Test that the list of categories is correctly returned to an unauthenticated user with the categories_with_videos action.
            The returned list should contain the names of the categories, and the videos in each category. """
            
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        category_names = [cat['name'] for cat in response.data]
        self.assertIn(self.category1.name, category_names)
        self.assertIn(self.category2.name, category_names)