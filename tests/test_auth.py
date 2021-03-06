from django import test
from authentication import models as auth_models


AUTH_API_BASE_URL = "/auth/api"


class AuthAPITestCase(test.TestCase):

    def setUp(self):
        """Setup for test the authentication API endpoints
        """
        self.user = auth_models.User.objects.create(
            username='tester',
            password='QWERTY!@#',
            email='tester.user@email.com',
            first_name='Tester',
            last_name='User',
            is_superuser=True,
        )
        self.user.set_password('QWERTY!@#')
        self.user.save()
        self.client = test.Client()

    def test_login_with_valid_credentials(self):
        """Test login endpoint with valid credentials
        """
        response = self.client.post(
            path=AUTH_API_BASE_URL + '/login/',
            data={'username': 'tester', 'password': 'QWERTY!@#'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)

    def test_login_with_invalid_credentials(self):
        """Test login endpoint with invalid credentials
        """
        response = self.client.post(
            path=AUTH_API_BASE_URL + '/login/',
            data={'username': 'tester', 'password': 'qwerty123'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_logout(self):
        """Test logout endpoint
        """
        self.client.force_login(self.user)
        response = self.client.get(path=AUTH_API_BASE_URL+'/logout/')
        self.assertEqual(response.status_code, 200)

    def test_registration_with_valid_credentials(self):
        """Test the registration endpoint with valid credentials
        """
        response = self.client.post(
            path=AUTH_API_BASE_URL + '/register/',
            data={
                'first_name': 'William',
                'last_name': 'Fernandes',
                'email': 'william.fernandes@email.com',
                'username': 'william',
                'password': 'QWERTY!@#',
                'password2': 'QWERTY!@#',
            },
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)

    def test_registration_with_invalid_credentials(self):
        """Test the registration endpoint with invalid credentials
        """
        response = self.client.post(
            path=AUTH_API_BASE_URL + '/register/',
            data={
                'first_name': 'William',
                'last_name': 'Fernandes',
                'email': 'william.fernandes@email.com',
                'username': 'william',
                'password': 'QWERTY!@#',
                'password2': 'qwerty123',
            },
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_registration_with_missing_fields(self):
        """Test the registration endpoint with missing fields.
        """
        response = self.client.post(
            path=AUTH_API_BASE_URL + '/register/',
            data={
                'first_name': 'William',
                'last_name': 'Fernandes',
                'email': 'william.fernandes@email.com',
                'username': 'william',
                'password': 'QWERTY!@#',
            },
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_login_with_registered_user(self):
        """Test the login endpoint with user registered with register endpoint
        """
        registration_response = self.client.post(
            path=AUTH_API_BASE_URL + '/register/',
            data={
                'first_name': 'William',
                'last_name': 'Fernandes',
                'email': 'william.fernandes@email.com',
                'username': 'william',
                'password': 'QWERTY!@#',
                'password2': 'QWERTY!@#',
            },
            content_type='application/json',
        )
        login_response = self.client.post(
            path=AUTH_API_BASE_URL + '/login/',
            data={'username': 'william', 'password': 'QWERTY!@#'},
            content_type='application/json',
        )
        self.assertEqual(registration_response.status_code, 201)
        self.assertEqual(login_response.status_code, 200)
