import unittest
from monolith.app import create_app
from flask_test_with_csrf import FlaskClient
from flask import url_for
from flask_login import current_user
from utils import do_login, get_my_restaurant_id, get_restaurant_likes
from monolith.background import check_likes

class TestLogin(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.app = create_app("TEST")
        self.app.test_client_class = FlaskClient

    def test_likes(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client,"operator@example.com", "operator")
        rest_id = get_my_restaurant_id(client)
        self.assertIsNotNone(rest_id)
        likes = get_restaurant_likes(client, rest_id)
        self.assertIsNotNone(likes)
        self.assertEqual("42", likes)
        
    def test_likes(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client,"operator@example.com", "operator")
        rest_id = get_my_restaurant_id(client)
        self.assertIsNotNone(rest_id)

        check_likes.apply()

        likes = get_restaurant_likes(client, rest_id)
        self.assertIsNotNone(likes)
        self.assertEqual("43", likes)
