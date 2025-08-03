from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

class PasswordResetConfirmTests(APITestCase):

    def setUp(self):
        """ Set up the test case. Create a test user, get a base64 encoded version of the user's primary key, 
        generate a password reset token, and construct the URL for the password reset confirm endpoint.    """

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='old_password123',
            is_active=True
        )
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
        self.url = reverse('password_confirm', kwargs={'uidb64': self.uidb64, 'token': self.token})


    def test_password_reset_confirm_success(self):
        """Tests a successful password reset. Verifies that the response returns HTTP 200 status, includes the 'detail' key in the response body, 
        and that the user's password has been changed to the new password.    """
        
        data = {
            'new_password': 'new_secure_password',
            'repeat_password': 'new_secure_password',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "Your Password has been successfully reset.")       
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('new_secure_password'))


    def test_passwords_do_not_match(self):
        """Tests that a password reset attempt with mismatched passwords returns a 400 status
        code and includes 'non_field_errors' in the response data, indicating validation failure."""

        data = {
            'new_password': 'new_password1',
            'repeat_password': 'new_password2',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)  


    def test_invalid_uid(self):
        """Tests that a password reset attempt with an invalid user id returns a 400 status
        code and includes 'non_field_errors' in the response data, indicating validation failure."""
        
        invalid_uid = urlsafe_base64_encode(force_bytes(999999)) 
        url = reverse('password_confirm', kwargs={'uidb64': invalid_uid, 'token': self.token})
        data = {
            'new_password': 'new_secure_password',
            'repeat_password': 'new_secure_password',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)


    def test_invalid_token(self):
        """Tests that a password reset attempt with an invalid token returns a 400 status code and includes 'non_field_errors' 
        in the response data, indicating validation failure."""
        
        invalid_token = 'invalid-token-123'
        url = reverse('password_confirm', kwargs={'uidb64': self.uidb64, 'token': invalid_token})
        data = {
            'new_password': 'new_secure_password',
            'repeat_password': 'new_secure_password',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)


    def test_missing_uid_or_token(self):
        """Tests that a password reset attempt with missing or invalid UID and token returns a 400 status code and includes 
        'non_field_errors' in the response data, indicating validation failure."""

        url = reverse('password_confirm', kwargs={'uidb64': 'invalid_uid', 'token': 'invalid_token'})
        data = {
            'new_password': 'new_secure_password',
            'repeat_password': 'new_secure_password',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)