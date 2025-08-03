from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

class RegisterTests(APITestCase):

    def test_register_success(self):
        """ Tests that a successful registration returns HTTP 201 CREATED status, a user object with 'id' and 'email', and a token in the response data. 
        Verifies that the new user is created in the database. """
        
        url = reverse('register')  
        data = {
            'email': 'newuser@example.com',
            'password': 'strongpassword123',
            'confirmed_password': 'strongpassword123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('id', response.data['user'])
        self.assertEqual(response.data['user']['email'], 'newuser@example.com')
        self.assertIn('token', response.data)       
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())


    def test_register_passwords_do_not_match(self):
        """Tests that a registration attempt with non-matching passwords returns a 400 status code 
        and includes 'password' in the response data, indicating the error."""

        url = reverse('register')
        data = {
            'email': 'user@example.com',
            'password': 'password123',
            'confirmed_password': 'password456'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)


    def test_register_password_too_short(self):
        """Tests that a registration attempt with a password that is too short returns a 400 status code
        and includes 'password' in the response data, indicating the error."""

        url = reverse('register')
        data = {
            'email': 'user@example.com',
            'password': '123',
            'confirmed_password': '123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)


    def test_register_email_already_exists(self):
        """Tests that a registration attempt with an email that already exists returns a 400 status code
        and includes 'email' in the response data, indicating the email is already registered."""

        User.objects.create_user(username='user', email='user@example.com', password='password123')
        url = reverse('register')
        data = {
            'email': 'user@example.com',
            'password': 'newpassword123',
            'confirmed_password': 'newpassword123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)