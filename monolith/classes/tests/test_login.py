import unittest
from monolith.app import create_app
from flask import url_for
app = create_app()

app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False
#app.config['SERVER_NAME'] = False

class TestLogin(unittest.TestCase):

    def test_login_get_1(self):
        tested_app = app.test_client()
        reply = tested_app.get('/login')
        self.assertTrue("form" in reply.get_data(as_text=True))

    def test_login_post_admin(self):
        TESTING = True
        WTF_CSRF_ENABLED = False
        tested_app = app.test_client()
        reply = tested_app.post('/login',data={"email":"example@example.com", "password": "admin"})
        with app.test_request_context():
            self.assertEqual(reply.location, url_for('home.index',_external=True))