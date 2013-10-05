from django.test import TestCase
from django.test.client import Client
from core.models import User


class Login_Test(TestCase):
    fixtures = ['test_users.json']

    def test_forbidden_access(self):
        """Go to site withoug logged in."""
        self.client = Client()
        response = self.client.get('/')
        self.assertRedirects(response, '/login?next=/') 

    def test_login(self):
        """Log in."""
        self.client = Client()
        response = self.client.post('/login', {'username':'root','password':'toto'})
        self.assertRedirects(response, '/') 
        self.assertEqual(response.status_code, 302, 'Bad response code from login page')

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200, "Logged in user can't access to website.")

    def test_logout(self):
        """Log out."""
        self.client = Client()
        response = self.client.post('/login', {'username':'root','password':'toto'})

        response = self.client.get('/logout')
        self.assertRedirects(response, '/login') 

        response = self.client.get('/')
        self.assertNotEqual(response.status_code, 200, "User can access after logout")
