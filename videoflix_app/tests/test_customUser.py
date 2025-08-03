from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class CustomUserModelTest(APITestCase):
    def setUp(self):
        """ Create a user, and an APIClient that is authenticated with that user.
            This is done so that we can test the user's profile. """
            
        self.user = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123',
            first_name='OldName',
            last_name='Last',
            address='Old Address',
            phone='123456789'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)


    def test_create_user_with_extra_fields(self):
        """ Tests that a user can be created with extra fields."""
        
        user = User.objects.get(username='user1')
        self.assertEqual(user.first_name, 'OldName')
        self.assertEqual(user.address, 'Old Address')
        self.assertEqual(user.phone, '123456789')
    
    
    def test_get_user_profile(self):
        """ Tests that the user's profile can be retrieved. The first name is
           verified to ensure that the correct user is being returned."""
           
        url = reverse('user-me')
        response = self.client.get(url)        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'OldName')


    def test_update_user_profile_patch(self):
        """ Tests that a user's profile can be partially updated using the PATCH method."""
        
        url = reverse('user-me')
        data = {
            'first_name': 'NewName',
            'address': 'New Address'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'NewName')
        self.assertEqual(response.data['address'], 'New Address')


    def test_update_user_profile_put(self):
        """ Tests that a user's profile can be fully updated using the PUT method."""

        url = reverse('user-me')
        data = {
            'first_name': 'CompleteName',
            'last_name': 'UpdatedLast',
            'address': 'Completely New Address',
            'phone': '987654321'
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'CompleteName')
        self.assertEqual(response.data['last_name'], 'UpdatedLast')


    def test_delete_user_not_allowed(self):
        """ Tests that attempting to delete a user account results in a 405 Method Not Allowed response."""

        url = reverse('user-detail', kwargs={'pk': self.user.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Deleting account is not allowed.')
        
    def test_get_user_profile_unauthenticated(self):
        """ Tests that attempting to retrieve a user's profile when not authenticated results in a 401 Unauthorized response."""
        
        self.client.force_authenticate(user=None)  
        url = reverse('user-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_patch_user_profile_unauthenticated(self):
        """ Tests that attempting to partially update a user's profile when not authenticated results in a 401 Unauthorized response."""
        
        self.client.force_authenticate(user=None) 
        url = reverse('user-me')
        response = self.client.patch(url, {'first_name': 'ShouldFail'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)