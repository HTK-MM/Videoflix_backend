from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()
class LogoutTests(APITestCase):

    def setUp(self):       
        """ Sets up the test case.
        Creates a test user, a refresh token, and the logout url. 
        :return : None   """
        
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.refresh = RefreshToken.for_user(self.user)
        self.url = reverse('logout')


    def test_logout_success(self):        
        """Tests a successful logout. Verifies that the response returns HTTP 200 status, 
        includes the 'detail' key in the response body, and that both 'access_token' and 
        'refresh_token' are set as expired cookies. """
        
        self.client.cookies['refresh_token'] = str(self.refresh)        
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid.")
       
        self.assertIn('access_token', response.cookies)
        self.assertEqual(response.cookies['access_token']['max-age'], 0)
        self.assertIn('refresh_token', response.cookies)
        self.assertEqual(response.cookies['refresh_token']['max-age'], 0)


    def test_logout_missing_refresh_token(self):       
        """ Tests that a logout attempt without a refresh token returns a 400 status code
        and an appropriate error message indicating the missing refresh token."""

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('error'), "Refresh token is missing.")


    def test_logout_invalid_refresh_token(self):       
        """ Tests that a logout attempt with an invalid refresh token returns a 400 status code
        and an appropriate error message indicating the invalid or expired refresh token."""
        
        self.client.cookies['refresh_token'] = 'invalidtoken123'
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('error'), "Invalid or expired refresh token.")