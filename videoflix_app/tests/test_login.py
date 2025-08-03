from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class LoginTests(APITestCase):

    def setUp(self):
        """ Creates a user with username 'test', password 'securepass123', and email 'test@example.com'.
        This user is used in all tests in this class. """
        
        self.user = User.objects.create_user(    
            username='test',                                         
            password='securepass123',
            email='test@example.com'
        )
        
        
    def test_login_successful(self):
        """Tests a successful login. Verifies that the response returns HTTP 200 status, 
        includes both 'detail' and 'user' keys in the response body, and that 'access_token' and 
        'refresh_token' are correctly set as HttpOnly cookies. """
        
        url = reverse('login')
        data = {'email': 'test@example.com', 'password': 'securepass123'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        self.assertIn('user', response.data)
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)
        self.assertTokenCookiesSet(response)
       
        
    def assertTokenCookiesSet(self, response):
        """ Asserts that the 'access_token' and 'refresh_token' are present in the response cookies
        and that both cookies are set as HttpOnly, ensuring they are only accessible via HTTP(S)."""

        self.assertIn('access_token', response.cookies)
        self.assertTrue(response.cookies['access_token']['httponly'])
        self.assertIn('refresh_token', response.cookies)
        self.assertTrue(response.cookies['refresh_token']['httponly'])
       
        
    def test_login_invalid_password(self):
        """Tests that an invalid password for a registered email returns a 400 status
        code and does not set any of the 'access_token' or 'refresh_token' cookies."""
        
        url = reverse('login')
        data = {'email': 'test@example.com', 'password': 'wrongpass'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_login_email_not_registered(self):
        """Tests that a login attempt with an unregistered email returns a 400 status
        code, indicating that the email is not recognized in the system."""

        url = reverse('login')
        data = {'email': 'noexist@example.com', 'password': 'any'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)