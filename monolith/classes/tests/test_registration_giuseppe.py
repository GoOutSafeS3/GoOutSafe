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


    # --- CREATE_USER -------------------------------------------------------

    def test_user_good_form(self):
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

        reply = self.send_registration_form(tested_app, '/create_user', form)
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'success, User registerd succesfully') 

    def test_user_regood_form(self):
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

        reply = self.send_registration_form(tested_app, '/create_user', form)
        
        self.assertEqual(
            reply["status_code"],
            400,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'error, Existing user')

    def test_user_missing_field(self):
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

            reply = self.send_registration_form(tested_app, '/create_user', form)
            
            self.assertEqual(
                reply["status_code"],
                200,msg=reply)
            self.assertEqual(
                reply["help-block"],
                'This field is required.')

    def test_user_empty_field(self):
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

            reply = self.send_registration_form(tested_app, '/create_user', form)
            
            self.assertEqual(
                reply["status_code"],
                200,msg=reply)
            self.assertEqual(
                reply["help-block"],
                'This field is required.')

    def test_user_empty_field(self):
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
                tested_form[f] = None

                reply = self.send_registration_form(tested_app, '/create_user', form)
                
                self.assertEqual(
                    reply["status_code"],
                    200,msg=reply)
                self.assertEqual(
                    reply["help-block"],
                    'This field is required.')

    def test_user_existing_email(self):
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

        reply = self.send_registration_form(tested_app, '/create_user', form)

        self.assertEqual(
            reply["status_code"],
            400,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'error, Existing user')

    def test_user_existing_name_surname(self):
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

        reply = self.send_registration_form(tested_app, '/create_user', form)
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply) 
        self.assertEqual(
            reply["help-block"],
            'success, User registerd succesfully') 

    def test_user_wrong_dateofbirth(self):
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

        reply = self.send_registration_form(tested_app, '/create_user', form)
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'Not a valid date value')

    def test_user_wrong_repeated_password(self):
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

        reply = self.send_registration_form(tested_app, '/create_user', form)
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'warning, Passwords do not match')

    def test_user_wrong_email(self):
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

        reply = self.send_registration_form(tested_app, '/create_operator', form)
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'Invalid email address.')

    def test_user_wrong_telephone_form(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        form = {
            "email":"testerWrongTelephone@test.me",
            "firstname":"Tester",
            "lastname":"WT",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"thisisatelephone",
        }

        reply = self.send_registration_form(tested_app, '/create_user', form)
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'Not a valid integer value') 

    # --- CREATE_OPERATOR -------------------------------------------------------

    def test_operator_good_form(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        form = {
            "email":"testerGoodFormOperator@test.me",
            "firstname":"Tester",
            "lastname":"GF",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
            "restaurant_name":"Restaurant at the End of the Universe",
            "restaurant_phone":"1234567890",
            "restaurant_latitude":"43.431489",
            "restaurant_longitude":"10.242911",
        }

        reply = self.send_registration_form(tested_app, '/create_operator', form)
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'success, Operator registerd succesfully') 

    def test_operator_regood_form(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        form = {
            "email":"testerGoodFormOperatorm@test.me",
            "firstname":"Tester",
            "lastname":"GF",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
            "restaurant_name":"Restaurant at the End of the Universe",
            "restaurant_phone":"1234567890",
            "restaurant_latitude":"43.431489",
            "restaurant_longitude":"10.242911",
        }

        reply = self.send_registration_form(tested_app, '/create_operator', form)
        
        self.assertEqual(
            reply["status_code"],
            400,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'error, Existing restaurant')

    def test_operator_same_operator_form(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        form = {
            "email":"testerGoodFormOperator@test.me",
            "firstname":"Tester",
            "lastname":"GF",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
            "restaurant_name":"The Restaurant (almost) at the End of the Universe",
            "restaurant_phone":"1234567890",
            "restaurant_latitude":"43.431489",
            "restaurant_longitude":"10.242911",
        }

        reply = self.send_registration_form(tested_app, '/create_operator', form)
        
        self.assertEqual(
            reply["status_code"],
            400,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'error, Existing operator')

    def test_operator_missing_field(self):
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
            "restaurant_name":"The Restaurant at the End of the Universe",
            "restaurant_phone":"1234567890",
            "restaurant_latitude":"43.431489",
            "restaurant_longitude":"10.242911",
        }

        fields = ["email","firstname","lastname","password","dateofbirth","telephone","password_repeat","restaurant_name","restaurant_phone","restaurant_latitude","restaurant_longitude"]

        for f in fields:
            tested_form = form
            del tested_form[f]

            reply = self.send_registration_form(tested_app, '/create_operator', form)
            
            self.assertEqual(
                reply["status_code"],
                200,msg=reply)
            self.assertEqual(
                reply["help-block"],
                'This field is required.')

    def test_operator_empty_field(self):
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
            "restaurant_name":"The Restaurant at the End of the Universe",
            "restaurant_phone":"1234567890",
            "restaurant_latitude":"43.431489",
            "restaurant_longitude":"10.242911",
        }

        fields = ["email","firstname","lastname","password","dateofbirth","telephone","password_repeat","restaurant_name","restaurant_phone","restaurant_latitude","restaurant_longitude"]

        for f in fields:
            tested_form = form
            tested_form[f] = ""

            reply = self.send_registration_form(tested_app, '/create_operator', form)
            
            self.assertEqual(
                reply["status_code"],
                200,msg=reply)
            self.assertEqual(
                reply["help-block"],
                'This field is required.')

    def test_operator_none_field(self):
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
                "restaurant_name":"The Restaurant at the End of the Universe",
                "restaurant_phone":"1234567890",
                "restaurant_latitude":"43.431489",
                "restaurant_longitude":"10.242911",
            }

            fields = ["email","firstname","lastname","password","dateofbirth","telephone","password_repeat","restaurant_name","restaurant_phone","restaurant_latitude","restaurant_longitude"]

            for f in fields:
                tested_form = form
                tested_form[f] = None

                reply = self.send_registration_form(tested_app, '/create_operator', form)
                
                self.assertEqual(
                    reply["status_code"],
                    200,msg=reply)
                self.assertEqual(
                    reply["help-block"],
                    'This field is required.')

    def test_operator_existing_email(self):
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
            "restaurant_name":"The Restaurant at the End of the Universe",
            "restaurant_phone":"1234567890",
            "restaurant_latitude":"43.431489",
            "restaurant_longitude":"10.242911",
        }

        reply = self.send_registration_form(tested_app, '/create_operator', form)

        self.assertEqual(
            reply["status_code"],
            400,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'error, Existing operator')

    def test_operator_existing_name_surname(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        form = {
            "email":"testerExistingNameSurnameOperator@tester.com",
            "firstname":"Tester",
            "lastname":"GF",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
            "restaurant_name":"The Restaurant at the End of the Universe",
            "restaurant_phone":"1234567890",
            "restaurant_latitude":"43.431489",
            "restaurant_longitude":"10.242911",
        }

        reply = self.send_registration_form(tested_app, '/create_operator', form)
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply) 
        self.assertEqual(
            reply["help-block"],
            'success, Operator registerd succesfully') 

    def test_operator_wrong_dateofbirth(self):
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
            "restaurant_name":"The Restaurant at the End of the Universe",
            "restaurant_phone":"1234567890",
            "restaurant_latitude":"43.431489",
            "restaurant_longitude":"10.242911",
        }

        reply = self.send_registration_form(tested_app, '/create_operator', form)
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'Not a valid date value')

    def test_operator_wrong_repeated_password(self):
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
            "restaurant_name":"The Restaurant at the End of the Universe",
            "restaurant_phone":"1234567890",
            "restaurant_latitude":"43.431489",
            "restaurant_longitude":"10.242911",
        }

        reply = self.send_registration_form(tested_app, '/create_operator', form)
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'warning, Passwords do not match')

    def test_operator_wrong_email(self):
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
            "restaurant_name":"The Restaurant at the End of the Universe",
            "restaurant_phone":"1234567890",
            "restaurant_latitude":"43.431489",
            "restaurant_longitude":"10.242911",
        }

        reply = self.send_registration_form(tested_app, '/create_operator', form)
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'Invalid email address.')

    def test_user_wrong_operator_telephone_form(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        form = {
            "email":"testerWrongTelephoneNumber@test.me",
            "firstname":"Tester",
            "lastname":"WT",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"thisisatelephonenumber",
            "restaurant_name":"The Restaurant at the End of the Universe",
            "restaurant_phone":"1234567890",
            "restaurant_latitude":"43.431489",
            "restaurant_longitude":"10.242911",
        }

        reply = self.send_registration_form(tested_app, '/create_operator', form)
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'Not a valid integer value') 

    def test_user_wrong_rest_telephone_form(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        form = {
            "email":"testerWrongTelephoneNumber@test.me",
            "firstname":"Tester",
            "lastname":"WT",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
            "restaurant_name":"The Restaurant at the End of the Universe",
            "restaurant_phone":"thisisatelephonenumber",
            "restaurant_latitude":"43.431489",
            "restaurant_longitude":"10.242911",
        }

        reply = self.send_registration_form(tested_app, '/create_operator', form)
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'Not a valid integer value') 

    def test_user_wrong_latitude_form(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        form = {
            "email":"testerWrongTelephoneNumber@test.me",
            "firstname":"Tester",
            "lastname":"WT",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
            "restaurant_name":"The Restaurant at the End of the Universe",
            "restaurant_phone":"1234567890",
            "restaurant_latitude":"latitude",
            "restaurant_longitude":"10.242911",
        }

        reply = self.send_registration_form(tested_app, '/create_operator', form)
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'Not a valid float value') 

    def test_user_wrong_longitude_form(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        form = {
            "email":"testerWrongTelephoneNumber@test.me",
            "firstname":"Tester",
            "lastname":"WT",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
            "restaurant_name":"The Restaurant at the End of the Universe",
            "restaurant_phone":"1234567890",
            "restaurant_latitude":"43.431489",
            "restaurant_longitude":"longitude",
        }

        reply = self.send_registration_form(tested_app, '/create_operator', form)
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'Not a valid float value') 

 # --- USERS LIST --------------------------------------------------------
    
    def test_get_users_as_anonymous(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        reply = tested_app.get('/users')
        
        self.assertEqual(
            reply.status_code,
            401,msg=reply)

    def test_get_users_as_user(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        tested_app.t_post('/login',data={"email":"testerGoodForm@test.me", "password": "42"})

        reply = tested_app.get('/users')
        
        self.assertEqual(
            reply.status_code,
            401,msg=reply)

    def test_get_users_as_operator(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        tested_app.t_post('/login',data={"email":"testerGoodFormOperator@test.me", "password": "42"})

        reply = tested_app.get('/users')
        
        self.assertEqual(
            reply.status_code,
            401,msg=reply)

    def test_get_users_as_admin(self):
        tested_app = app.test_client()
        tested_app.set_app(app)

        tested_app.t_post('/login',data={"email":"example@example.com", "password": "admin"})

        reply = tested_app.get('/users')
        html = reply.get_data(as_text=True)
        self.assertEqual(
            reply.status_code,
            200,msg=html)
        self.assertIn("Admin Admin",html,msg=html)
        self.assertIn("Tester GF",html,msg=html)


if __name__ == '__main__':
    unittest.main()