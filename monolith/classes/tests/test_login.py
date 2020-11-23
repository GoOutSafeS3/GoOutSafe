import unittest
from monolith.app import create_app
from flask_test_with_csrf import FlaskClient
from flask import url_for
from flask_login import current_user
from utils import do_login, do_logout

class TestLogin(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.app = create_app("TEST")
        self.app.test_client_class = FlaskClient

    def test_login_get_1(self):
        client = self.app.test_client()
        client.set_app(self.app)
        reply = client.t_get('/login')
        self.assertEqual(reply.status_code, 200, msg=reply.get_data(as_text=True))
        self.assertTrue("form" in reply.get_data(as_text=True))

    def test_login_post_admin(self):
        client = self.app.test_client()
        client.set_app(self.app)
        reply = do_login(client, "admin@example.com","admin")
        self.assertEqual(reply.status_code, 302)
        with self.app.test_request_context():
            self.assertEqual(reply.location, url_for('home.index',_external=True))

    def test_login_post_wrong(self):
        client = self.app.test_client()
        client.set_app(self.app)
        reply = do_login(client, "admin@example.com","wrong")
        self.assertEqual(reply.status_code, 401)

    def test_login_post_wrong2(self):
        client = self.app.test_client()
        client.set_app(self.app)
        reply = do_login(client, "admin@wrong.com","admin")
        self.assertEqual(reply.status_code, 401)

    def test_login_post_bad(self):
        client = self.app.test_client()
        client.set_app(self.app)
        reply = do_login(client, "admin@example.com",None)
        self.assertEqual(reply.status_code, 400)

    def test_login_logout(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            reply = do_login(client, "admin@example.com", "admin")
            self.assertEqual(current_user.is_authenticated, True)

            reply = do_logout(client)
            self.assertEqual(current_user.is_authenticated, False)
