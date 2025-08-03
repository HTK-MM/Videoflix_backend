from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()

class PasswordResetTests(APITestCase):
    def setUp(self):
        """  Creates a test user and sets the password reset URL. 
        :return : None """
        
        self.user = User.objects.create_user(
            username='test',
            email='test@example.com', 
            password='testpass123'
        )
        self.url = reverse('password_reset')


    @patch('videoflix_app.api.views.get_queue') 
    def test_password_reset_request_success(self, mock_get_queue):
        """Tests that a password reset request for a registered email is successful. 
        Mocks the background task queue to verify that the email is enqueued for sending. Asserts that the response status code is 200 OK, and that 
        the 'detail' key is in the response data. Additionally, verifies that the email sending task is enqueued exactly once."""

        mock_queue = mock_get_queue.return_value
        mock_queue.enqueue.return_value = None 
        response = self.client.post(self.url, {'email': self.user.email})        
        self.assertEqual(response.status_code, status.HTTP_200_OK)       
        self.assertIn('detail', response.data)
        mock_queue.enqueue.assert_called_once()  
        

    def test_password_reset_request_invalid_email(self):
        """Tests that a password reset request for an invalid email returns HTTP 400 BAD REQUEST status, and that the 'email' key is in the response data."""
        
        response = self.client.post(self.url, {'email': 'notanemail'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


    @patch('videoflix_app.api.views.get_queue')
    def test_password_reset_request_unregistered_email(self, mock_get_queue):    
        """ Tests that a password reset request for an unregistered email returns HTTP 200 OK status, that the 'detail' key is in the response data, 
        and that the email sending task is not enqueued."""
        
        response = self.client.post(self.url, {'email': 'unknown@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)       
        self.assertIn('detail', response.data)
        mock_get_queue.return_value.enqueue.assert_not_called()

    