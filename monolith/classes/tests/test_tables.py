import unittest
from monolith.app import create_app_testing
from flask_test_with_csrf import FlaskClient
from flask import url_for
from flask_login import current_user
from utils import do_login, get_restaurant_id

class TestLogin(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.app = create_app_testing()
        self.app.test_client_class = FlaskClient

    def test_list_tables(self):
        client = self.app.test_client()
        client.set_app(self.app)
        reply = do_login(client, "customer@example.com", "customer")
        id = get_restaurant_id(client)
        self.assertIsNotNone(id)
