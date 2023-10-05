from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
# Create your tests here.


def create_super_user():
    user = User.objects.create_superuser('admin', 'admin@example.com', '123')
    return user


def create_user():
    user = User.objects.create_user('customer', 'customer@example.com', '1234')
    return user


def make_groups():
    Group.objects.create(name='staff')
    Group.objects.create(name='orgs')
    Group.objects.create(name='customer')


class TokenTests(TestCase):

    def test_getting_token_with_valid_auth(self):
        user = create_super_user()
        response = self.client.post(reverse('token-obtain-pair'), {'username': user.username, 'password': '123'})
        self.assertEqual(response.status_code, 200)

    def test_getting_token_with_wrong_password(self):
        user = create_super_user()
        response = self.client.post(reverse('token-obtain-pair'), {'username': user.username, 'password': '321'})
        self.assertEqual(response.status_code, 401)

    def test_getting_token_with_wrong_username(self):
        user = create_super_user()
        response = self.client.post(reverse('token-obtain-pair'), {'username': user.username+'1', 'password': '123'})
        self.assertEqual(response.status_code, 401)


class UserModelsTests(TestCase):

    def get_access_token(self, username='admin', password='123'):
        response = self.client.post(reverse('token-obtain-pair'), {'username': username, 'password': password})
        return response.json()['access']

    def get_response(self, url, token):
        return self.client.get(url, format='json',
                               **{'HTTP_AUTHORIZATION': f'Bearer {token}'}, follow=True)

    def post_response(self, url, data, token):
        return self.client.post(url, data=data, format='json',
                                **{'HTTP_AUTHORIZATION': f'Bearer {token}'}, follow=True)

    def test_users_list_with_superuser(self):
        create_super_user()
        token = self.get_access_token()
        response = self.get_response(reverse('users_list'), token)
        self.assertEqual(response.status_code, 200)

    def test_user_list_with_not_superuser(self):
        create_user()
        token = self.get_access_token(username='customer', password='1234')
        response = self.get_response(reverse('users_list'), token)
        self.assertEqual(response.status_code, 403)

    def test_user_list_without_auth(self):
        create_super_user()
        token = self.get_access_token()
        response = self.get_response(reverse('users_list'), token[:-1])
        self.assertEqual(response.status_code, 401)

    def test_view_another_user_by_superuser(self):
        create_super_user()
        user = create_user()
        token = self.get_access_token()
        response = self.get_response(reverse('view-user', args=(user.id,)), token)
        self.assertEqual(response.status_code, 200)

    def test_view_user_by_another_user(self):
        user1 = create_user()
        user2 = User.objects.create_user(username='customer2', email=None, password='12345')
        token = self.get_access_token(username=user2.username, password='12345')
        response = self.get_response(reverse('view-user', args=(user1.id,)), token)
        self.assertEqual(response.status_code, 403)

    def test_view_user_by_himself(self):
        user = create_user()
        token = self.get_access_token(username=user.username, password='1234')
        response = self.get_response(reverse('view-user', args=(user.id,)), token)
        self.assertEqual(response.status_code, 200)

    def test_register_user(self):
        make_groups()
        user = create_super_user()
        token = self.get_access_token(username=user.username, password='123')
        data = {"username": "customer", "password": "12345678!", "password2": "12345678!",
                "email": "customer@example.com",
                "first_name": "a", "last_name": "b", "group": "staff"}
        response = self.post_response(reverse('user-register'), data, token)
        self.assertEqual(response.status_code, 201)

    def test_register_customer_by_org(self):
        make_groups()
        user = create_super_user()
        token = self.get_access_token(username=user.username, password='123')
        data = {"username": "org", "password": "12345678!", "password2": "12345678!",
                "email": "org@example.com",
                "first_name": "a", "last_name": "b", "group": "orgs"}
        response = self.post_response(reverse('user-register'), data, token)
        self.assertEqual(response.status_code, 201)
        token = self.get_access_token(username='org', password='12345678!')
        data = {"username": "customer", "password": "12345678!", "password2": "12345678!",
                "email": "customer@example.com",
                "first_name": "a", "last_name": "b", "group": "customer"}
        response = self.post_response(reverse('user-register'), data, token)
        self.assertEqual(response.status_code, 201)

    def test_register_org_by_org(self):
        make_groups()
        user = create_super_user()
        token = self.get_access_token(username=user.username, password='123')
        data = {"username": "org", "password": "12345678!", "password2": "12345678!",
                "email": "org@example.com",
                "first_name": "a", "last_name": "b", "group": "orgs"}
        response = self.post_response(reverse('user-register'), data, token)
        self.assertEqual(response.status_code, 201)
        token = self.get_access_token(username='org', password='12345678!')
        data = {"username": "org2", "password": "12345678!", "password2": "12345678!",
                "email": "org2@example.com",
                "first_name": "a", "last_name": "b", "group": "orgs"}
        response = self.post_response(reverse('user-register'), data, token)
        self.assertEqual(response.status_code, 400)

    def test_register_staff_by_staff(self):
        make_groups()
        user = create_super_user()
        token = self.get_access_token(username=user.username, password='123')
        data = {"username": "admin2", "password": "12345678!", "password2": "12345678!",
                "email": "admin2@example.com",
                "first_name": "aa", "last_name": "bb", "group": "staff"}
        response = self.post_response(reverse('user-register'), data, token)
        self.assertEqual(response.status_code, 201)


class DNAServicesTests(TestCase):

    def get_access_token(self, username='admin', password='123'):
        response = self.client.post(reverse('token-obtain-pair'), {'username': username, 'password': password})
        return response.json()['access']

    def post_response(self, url, data, token):
        return self.client.post(url, data=data, format='json',
                                **{'HTTP_AUTHORIZATION': f'Bearer {token}'}, follow=True)

    def test_add_DNA_scoring_with_super_user(self):
        make_groups()
        create_super_user()
        user = create_user()
        token = self.get_access_token()
        data = {"service_description": "[\"ACTGACTGACTG\"]", "customer_id": user.id}
        response = self.post_response(reverse('add-service'), data, token)
        self.assertEqual(response.status_code, 201)

