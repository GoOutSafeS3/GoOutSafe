import unittest
import json
from flask import request, jsonify
from monolith.app import create_app_testing
from flask_test_with_csrf import FlaskClient
from bs4 import BeautifulSoup
import inspect

app = create_app_testing()
app.test_client_class = FlaskClient

class TestRegistration(unittest.TestCase):

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

    def test_good_form(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        reply = self.send_registration_form(tested_app,"testerGoodForm@test.me","Tester", "GF", "42","42","123456","01/01/1970")
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply)

    def test_existing_email(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        reply = self.send_registration_form(tested_app,"example@example.com","Tester", "EE", "42","42","123456","01/01/1970")

        self.assertEqual(
            reply["status_code"],
            400,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'error, Existing user')

    def test_existing_name_surname_user(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        reply = self.send_registration_form(tested_app,"testerExistingNameSurname@tester.com","Tester", "GF", "42","42","123456","01/01/1970")
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply) 
        self.assertEqual(
            reply["help-block"],
            '') 

    def test_wrong_dateofbirth(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        reply = self.send_registration_form(tested_app,"testerWrongDateOfBirth@test.me","Tester", "DoB", "42","42","123456","thisisadateofbirth")
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply) #GB to change in 400?
        self.assertEqual(
            reply["help-block"],
            'Not a valid date value')

    def test_wrong_repeated_password(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        reply = self.send_registration_form(tested_app,"testerWrongRepeatedPassword@test.me","Tester", "WRP", "42","43","123456","01/01/1970")
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply) #GB to change in 400?
        self.assertEqual(
            reply["help-block"],
            'warning, Passwords do not match')

    def test_wrong_email(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        reply = self.send_registration_form(tested_app,"testerWorngEmail.test.me","tester", "WE", "42","42","123456","123456""01/01/1970")
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply) #GB 200 like dateofbirth or 400?
        self.assertEqual(
            reply["help-block"],
            'Invalid email address.') #GB Need a control like this


if __name__ == '__main__':
    unittest.main()