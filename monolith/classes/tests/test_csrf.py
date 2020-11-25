import unittest
from monolith.app import create_app
from flask_test_with_csrf import FlaskClient
from utils import send_registration_form
app = create_app()
app.test_client_class = FlaskClient

class TestLogin2(unittest.TestCase):

    def test_login2(self):
        # Now in your tests, you can request a test client the same way
        # that you normally do:
        tested_app = app.test_client()
        tested_app.set_app(app)
        # But now, `client` is an instance of the class we defined!

        form = {
            "email":"asadasddas@test.me",
            "firstname":"Tester",
            "lastname":"OGF",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"12345678900",
            "ssn": "",
        }

        reply = send_registration_form(tested_app,'/create_operator', form)
        self.assertEqual(
            reply["status_code"],
            302)