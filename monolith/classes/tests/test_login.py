import unittest
from monolith.app import create_app_testing
from flask_test_with_csrf import FlaskClient
from flask import url_for
app = create_app_testing()
app.test_client_class = FlaskClient
app.config['TESTING'] = True

class TestLogin(unittest.TestCase):

    def test_login_get_1(self):
        tested_app = app.test_client()
        tested_app.set_app(app)
        reply = tested_app.t_get('/login')
        self.assertEqual(reply.status_code, 200, msg=reply.get_data(as_text=True))
        self.assertTrue("form" in reply.get_data(as_text=True))

    def test_login_post_admin(self):
        tested_app = app.test_client()
        tested_app.set_app(app)
        reply = tested_app.t_post('/login',data={"email":"example@example.com", "password": "admin"})
        self.assertEqual(reply.status_code, 302)
        with app.test_request_context():
            self.assertEqual(reply.location, url_for('home.index',_external=True))

    def test_login_post_wrong(self):
        tested_app = app.test_client()
        tested_app.set_app(app)
        reply = tested_app.t_post('/login',data={"email":"example@example.com", "password": "wrong"})
        self.assertEqual(reply.status_code, 401)

    def test_login_post_bad(self):
        tested_app = app.test_client()
        tested_app.set_app(app)
        reply = tested_app.t_post('/login',data={"email":"example@example.com", "password": None})
        self.assertEqual(reply.status_code, 400)