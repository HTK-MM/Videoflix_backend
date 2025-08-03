from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

class UserActivationTests(APITestCase):
    def setUp(self):
        """Creates a user with username 'testuser', password 'testpass123', and email 'test@example.com'.
        This user is inactive and is used in all tests in this class."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_active=False
        )
    
    
    def test_activation_success(self):
        """Tests a successful user activation. Verifies that the response returns HTTP 200 OK status,
        the user's account is activated, and the response message confirms account activation."""

        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        url = reverse('activate-user', kwargs={'uidb64': uidb64, 'token': token})

        response = self.client.post(url)
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.is_active)
        self.assertEqual(response.data['message'], "Account successfully activated.")


    def test_activation_invalid_token(self):
        """Tests that a user activation attempt with an invalid token returns a 400 status code,
        the user's account remains inactive, and the response includes an error message indicating
        an invalid or expired token."""

        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        url = reverse('activate-user', kwargs={'uidb64': uidb64, 'token': 'invalid'})
        response = self.client.post(url)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.user.is_active)
        self.assertEqual(response.data.get('error'), 'Invalid or expired token')


    def test_activation_invalid_uid(self):
        """Tests that a user activation attempt with an invalid uid returns a 400 status code,
        the user's account remains inactive, and the response includes an error message indicating
        an invalid or expired uid."""

        token = default_token_generator.make_token(self.user)
        url = reverse('activate-user', kwargs={'uidb64': 'invalid', 'token': token})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('error'), 'Invalid UID')


    def test_activate_user_missing_data(self):        
        """Tests that a user activation attempt with missing UID and token returns a 400 status code,
        and the response includes an error message indicating an invalid UID."""

        url = reverse("activate-user", kwargs={"uidb64": 'invalid', "token": 'invalid'})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('error'), 'Invalid UID')        
        