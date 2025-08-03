from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

class TokenRefreshTests(APITestCase):

    def setUp(self):
        """ Sets up the test case.
        Creates a test user, a refresh token, and the URL for the token refresh endpoint. 
        :return : None   """
        
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='testpass123'
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.url = reverse('token_refresh') 


    def test_refresh_token_success(self):
        """Tests a successful token refresh. Verifies that the response returns HTTP 200 status, includes the 'message' key in the response body, 
        and that the 'access_token' is correctly set as a HttpOnly cookie."""
        
        self.client.cookies['refresh_token'] = str(self.refresh)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'access Token refreshed successfully')
        self.assertIn('access_token', response.cookies)
        self.assertTrue(response.cookies['access_token']['httponly'])


    def test_refresh_token_missing_cookie(self):
        """Tests that a token refresh request without a refresh token cookie returns a 400 status code
        and provides an appropriate error message indicating the missing refresh token."""

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('error'), 'Refresh token not found in cookies')


    def test_refresh_token_invalid_token(self):
        """Tests that a token refresh request with an invalid refresh token returns a 401 status code
        and provides an appropriate error message indicating the invalid refresh token."""
        
        self.client.cookies['refresh_token'] = 'invalidtoken123'
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get('detail'), 'Refresh token is invalid')