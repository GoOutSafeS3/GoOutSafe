import unittest
from monolith.app import create_app_testing
from flask_test_with_csrf import FlaskClient
from flask import url_for
app = create_app_testing()
app.test_client_class = FlaskClient
app.config['TESTING'] = True

class TestLogin(unittest.TestCase):

    def do_login(self,client, email, password):
        return client.t_post('/login',data={"email":email, "password": password})
        

    def test_login_get_1(self):
        client = app.test_client()
        client.set_app(app)
        reply = client.t_get('/login')
        self.assertEqual(reply.status_code, 200, msg=reply.get_data(as_text=True))
        self.assertTrue("form" in reply.get_data(as_text=True))

    def test_login_post_admin(self):
        client = app.test_client()
        client.set_app(app)
        reply = self.do_login(client, "example@example.com","admin")
        self.assertEqual(reply.status_code, 302)
        with app.test_request_context():
            self.assertEqual(reply.location, url_for('home.index',_external=True))

    def test_login_post_wrong(self):
        client = app.test_client()
        client.set_app(app)
        reply = self.do_login(client, "example@example.com","wrong")
        self.assertEqual(reply.status_code, 401)

    def test_login_post_wrong2(self):
        client = app.test_client()
        client.set_app(app)
        reply = self.do_login(client, "example@wrong.com","admin")
        self.assertEqual(reply.status_code, 401)

    def test_login_post_bad(self):
        client = app.test_client()
        client.set_app(app)
        reply = self.do_login(client, "example@example.com",None)
        self.assertEqual(reply.status_code, 400)