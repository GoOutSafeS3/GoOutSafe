import unittest
from monolith.app import create_app_testing
from flask_test_with_csrf import FlaskClient
from bs4 import BeautifulSoup

app = create_app_testing()
app.test_client_class = FlaskClient

class TestLogin2(unittest.TestCase):

    def send_registration_form(self,tested_app, email, firstname, lastname, password, password_repeat, telephone, dateofbirth):
        form = {
            "email":email,
            "firstname":firstname,
            "lastname":lastname,
            "password":password,
            "dateofbirth":dateofbirth,
            "telephone":telephone,
            "password_repeat":password_repeat,
        }
        
        reply = tested_app.t_post('/create_user', data=form)
        soup = BeautifulSoup(reply.get_data(as_text=True), 'html.parser')
        helpblock = soup.find_all('p', attrs={'class': 'help-block'})

        if helpblock == []:
            helpblock = ""
        else:
            helpblock = helpblock[0].text.strip()

        return {"status_code":reply.status_code, "help-block":helpblock}

    def test_login2(self):
        # Now in your tests, you can request a test client the same way
        # that you normally do:
        tested_app = app.test_client()
        tested_app.set_app(app)
        # But now, `client` is an instance of the class we defined!

        reply = self.send_registration_form(tested_app,"testerGoodForm@test.me","Tester", "GF", "42","42","123456","01/01/1970")
        self.assertEqual(
            reply["status_code"],
            200)
        self.assertEqual(
            reply["help-block"],
            '')