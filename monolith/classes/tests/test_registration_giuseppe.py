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

    def send_registration_form(self, tested_app, url, form):

        reply = tested_app.t_post(url, data=form)
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

        form = {
            "email":"testerGoodForm@test.me",
            "firstname":"Tester",
            "lastname":"GF",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
        }

        reply = self.send_registration_form(tested_app, form)
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply)

    def test_regood_form(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        form = {
            "email":"testerGoodForm@test.me",
            "firstname":"Tester",
            "lastname":"GF",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
        }
        reply = self.send_registration_form(tested_app, form)
        
        self.assertEqual(
            reply["status_code"],
            400,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'error, Existing user')

    def test_missing_field(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        form = {
            "email":"email@email.com",
            "firstname":"firstname",
            "lastname":"lastname",
            "password":"password",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
            "password_repeat":"password",
        }

        fields = ["email","firstname","lastname","password","dateofbirth","telephone","password_repeat"]

        for f in fields:
            tested_form = form
            del tested_form[f]

            reply = self.send_registration_form(tested_app, form)
            
            self.assertEqual(
                reply["status_code"],
                200,msg=reply)
            self.assertEqual(
                reply["help-block"],
                'This field is required.')

    def test_empty_field(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        form = {
            "email":"email@email.com",
            "firstname":"firstname",
            "lastname":"lastname",
            "password":"password",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
            "password_repeat":"password",
        }

        fields = ["email","firstname","lastname","password","dateofbirth","telephone","password_repeat"]

        for f in fields:
            tested_form = form
            tested_form[f] = ""

            reply = self.send_registration_form(tested_app, form)
            
            self.assertEqual(
                reply["status_code"],
                200,msg=reply)
            self.assertEqual(
                reply["help-block"],
                'This field is required.')

    def test_existing_email(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        form = {
            "email":"example@example.com",
            "firstname":"Tester",
            "lastname":"EE",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
        }

        reply = self.send_registration_form(tested_app, form)

        self.assertEqual(
            reply["status_code"],
            400,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'error, Existing user')

    def test_existing_name_surname_user(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        form = {
            "email":"testerExistingNameSurname@tester.com",
            "firstname":"Tester",
            "lastname":"GF",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
        }

        reply = self.send_registration_form(tested_app, form)
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply) 
        self.assertEqual(
            reply["help-block"],
            '') 

    def test_wrong_dateofbirth(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        form = {
            "email":"testerWrongDateOfBirth@test.me",
            "firstname":"Tester",
            "lastname":"DoB",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"thisisadateofbirth",
            "telephone":"1234567890",
        }

        reply = self.send_registration_form(tested_app, form)
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'Not a valid date value')

    def test_wrong_repeated_password(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        form = {
            "email":"testerWrongRepeatedPassword@test.me",
            "firstname":"Tester",
            "lastname":"WRP",
            "password":"42",
            "password_repeat":"43",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
        }

        reply = self.send_registration_form(tested_app, form)
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'warning, Passwords do not match')

    def test_wrong_email(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        form = {
            "email":"testerWorngEmail.test.me",
            "firstname":"Tester",
            "lastname":"WE",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
        }

        reply = self.send_registration_form(tested_app, form)
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'Invalid email address.')


if __name__ == '__main__':
    unittest.main()