import unittest
from monolith.app import create_app

app = create_app()
app.testing = True

class TestLogin(unittest.TestCase):

    def test_login_1(self):
        #TODO modify
        tested_app = app.test_client()
        reply = tested_app.get('/login').get_json()
        self.assertEqual(reply['result'], 'success')