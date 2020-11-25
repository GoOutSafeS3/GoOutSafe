import unittest
from flask import request, jsonify
from monolith.app import create_app
from flask_test_with_csrf import FlaskClient
from utils import send_registration_form


class TestRegistration(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.app = create_app()
        self.app.test_client_class = FlaskClient

    # --- CREATE_USER -------------------------------------------------------

    def test_user_good_form(self):
        tested_app = self.app.test_client()
        tested_app.set_app(self.app)

        form = {
            "email":"testerGoodForm@test.me",
            "firstname":"Tester",
            "lastname":"GF",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"01234567890",
            'ssn':None,
            'is_operator': False,
            'is_admin': False,
            'is_health_authority': False
        }

        reply = send_registration_form(tested_app, '/create_user', form)
        
        self.assertEqual(
            reply["status_code"],
            302,msg=reply)

        tested_app.t_post('/login', data={"email": "admin@example.com", "password": "admin"})
        resp = tested_app.get('/users')
        print(resp.get_json())

    def test_user_regood_form(self):
        tested_app = self.app.test_client()
        tested_app.set_app(self.app)

        form = {
            "email":"testerGoodForm@test.me",
            "firstname":"Tester",
            "lastname":"GF",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"01234567890",
            "ssn":None,
            'is_operator': False,
            'is_admin': False,
            'is_health_authority': False
        }

        reply = send_registration_form(tested_app, '/create_user', form)
        
        self.assertEqual(
            reply["status_code"],
            400,msg=reply)

    def test_user_missing_field(self):
        tested_app = self.app.test_client()
        tested_app.set_app(self.app)

        form = {
            "email":"email@email.com",
            "firstname":"firstname",
            "lastname":"lastname",
            "password":"password",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
            "password_repeat":"password",
            "ssn":None,
            'is_operator': False,
            'is_admin': False,
            'is_health_authority': False
        }

        fields = ["email","firstname","lastname","password","dateofbirth","telephone","password_repeat"]

        for f in fields:
            tested_form = form
            del tested_form[f]

            reply = send_registration_form(tested_app, '/create_user', form)
            
            self.assertEqual(
                reply["status_code"],
                302, msg=reply)
            

    def test_user_empty_field(self):
        tested_app = self.app.test_client()
        tested_app.set_app(self.app)

        form = {
            "email":"email@email.com",
            "firstname":"firstname",
            "lastname":"lastname",
            "password":"password",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
            "password_repeat":"password",
            "ssn": None,
            'is_operator': False,
            'is_admin': False,
            'is_health_authority': False
        }

        fields = ["email","firstname","lastname","password","dateofbirth","telephone","password_repeat"]

        for f in fields:
            tested_form = form
            tested_form[f] = ""

            reply = send_registration_form(tested_app, '/create_user', form)
            
            self.assertEqual(
                reply["status_code"],
                200,msg=reply)

    def test_user_none_field(self):
        tested_app = self.app.test_client()
        tested_app.set_app(self.app)

        form = {
            "email":"email@email.com",
            "firstname":"firstname",
            "lastname":"lastname",
            "password":"password",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
            "password_repeat":"password",
            "ssn":None,
            'is_operator': False,
            'is_admin': False,
            'is_health_authority': False
        }

        fields = ["email","firstname","lastname","password","dateofbirth","telephone","password_repeat"]

        for f in fields:
            tested_form = form
            tested_form[f] = None

            reply = send_registration_form(tested_app, '/create_user', form)
            
            self.assertEqual(
                reply["status_code"],
                200,msg=reply)

    def test_user_existing_email(self):
        tested_app = self.app.test_client()
        tested_app.set_app(self.app)

        form = {
            "email":"admin@example.com",
            "firstname":"Tester",
            "lastname":"EE",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
            "ssn":None,
            'is_operator': False,
            'is_admin': False,
            'is_health_authority': False
        }

        reply = send_registration_form(tested_app, '/create_user', form)

        self.assertEqual(
            reply["status_code"],
            400,msg=reply)

    def test_user_existing_name_surname(self):
        tested_app = self.app.test_client()
        tested_app.set_app(self.app)

        form = {
            "email":"testerExistingNameSurname@tester.com",
            "firstname":"Daniele",
            "lastname":"Verdi",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"12345678902",
            "ssn": None,
            'is_operator': False,
            'is_admin': False,
            'is_health_authority': False
        }

        reply = send_registration_form(tested_app, '/create_user', form)
        
        self.assertEqual(
            reply["status_code"],
            302,msg=reply) 

    def test_user_wrong_dateofbirth(self):
        tested_app = self.app.test_client()
        tested_app.set_app(self.app)

        form = {
            "email":"testerWrongDateOfBirth@test.me",
            "firstname":"Tester",
            "lastname":"DoB",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"thisisadateofbirth",
            "telephone":"1234567890",
            "ssn":None,
            'is_operator': False,
            'is_admin': False,
            'is_health_authority': False
        }

        reply = send_registration_form(tested_app, '/create_user', form)
        
        self.assertEqual(
            reply["status_code"],
            200, msg=reply)

    def test_user_wrong_repeated_password(self):
        tested_app = self.app.test_client()
        tested_app.set_app(self.app)

        form = {
            "email":"testerWrongRepeatedPassword@test.me",
            "firstname":"Tester",
            "lastname":"WRP",
            "password":"42",
            "password_repeat":"43",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
            "ssn": None,
            'is_operator': False,
            'is_admin': False,
            'is_health_authority': False
        }

        reply = send_registration_form(tested_app, '/create_user', form)
        
        self.assertEqual(
            reply["status_code"],
            400, msg=reply)

    def test_user_wrong_email(self):
        tested_app = self.app.test_client()
        tested_app.set_app(self.app)

        form = {
            "email":"testerWorngEmail.test.me",
            "firstname":"Tester",
            "lastname":"WE",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
            "ssn": None,
            'is_operator': False,
            'is_admin': False,
            'is_health_authority': False
        }

        reply = send_registration_form(tested_app, '/create_user', form)
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply)

    def test_user_with_ssn_form(self):
        tested_app = self.app.test_client()
        tested_app.set_app(self.app)

        form = {
            "email":"testerSSN@test.me",
            "firstname":"Tester",
            "lastname":"SSN",
            "password":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"0123456789001",
            "ssn":"0192837465HGTHUA",
            'is_operator': False,
            'is_admin': False,
            'is_health_authority': False
        }

        reply = send_registration_form(tested_app, '/create_user', form)
        
        self.assertEqual(
            reply["status_code"],
            302,msg=reply)

    def test_Z_user_with_ssn_form_existing(self):
        tested_app = self.app.test_client()
        tested_app.set_app(self.app)

        form = {
            "email":"testerSSN1@test.me",
            "firstname":"Tester",
            "lastname":"SSN",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"0123456789002",
            "ssn":"0192837465HGTHUA",
            'is_operator': False,
            'is_admin': False,
            'is_health_authority': False
        }

        reply = send_registration_form(tested_app, '/create_user', form)
        
        self.assertEqual(
            reply["status_code"],
            400,msg=reply)


    # --- CREATE_OPERATOR -------------------------------------------------------

    def test_operator_good_form(self):
        tested_app = self.app.test_client()
        tested_app.set_app(self.app)

        form = {
            "email":"testerGoodFormOperator@test.me",
            "firstname":"Tester",
            "lastname":"OGF",
            "password":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"12345678900",
            'is_operator':True,
            'is_admin':False,
            'is_health_authority':False,
            'ssn':None
        }

        reply = send_registration_form(tested_app, '/create_operator', form)
        
        self.assertEqual(
            reply["status_code"],
            302,msg=reply)

    def test_operator_existing_email(self):
        tested_app = self.app.test_client()
        tested_app.set_app(self.app)

        form = {
            "email":"admin@example.com",
            "firstname":"Tester",
            "lastname":"OEE",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
            'ssn':None,
            'is_operator': True,
            'is_admin': False,
            'is_health_authority': False
        }

        reply = send_registration_form(tested_app, '/create_operator', form)

        self.assertEqual(
            reply["status_code"],
            400,msg=reply)


    def test_operator_wrong_repeated_password(self):
        tested_app = self.app.test_client()
        tested_app.set_app(self.app)

        form = {
            "email":"testerWrongRepeatedPassword@test.me",
            "firstname":"Tester",
            "lastname":"OWRP",
            "password":"42",
            "password_repeat":"43",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
            'ssn':'CIAO6TRFGBHYFSDR',
            'is_operator': True,
            'is_admin': False,
            'is_health_authority': False
        }

        reply = send_registration_form(tested_app, '/create_operator', form)
        
        self.assertEqual(
            reply["status_code"],
            400,msg=reply)


 # --- USERS LIST --------------------------------------------------------
    
    def test_get_users_as_anonymous(self):
        tested_app = self.app.test_client()
        tested_app.set_app(self.app)

        reply = tested_app.get('/users')
        
        self.assertEqual(
            reply.status_code,
            401,msg=reply)

    def test_get_users_as_user(self):
        tested_app = self.app.test_client()
        tested_app.set_app(self.app)

        tested_app.t_post('/login',data={"email":"testerGoodForm@test.me", "password": "42"})

        reply = tested_app.get('/users')
        
        self.assertEqual(
            reply.status_code,
            401,msg=reply)

    def test_get_users_as_operator(self):
        tested_app = self.app.test_client()
        tested_app.set_app(self.app)

        tested_app.t_post('/login',data={"email":"testerGoodFormOperator@test.me", "password": "42"})

        reply = tested_app.get('/users')
        
        self.assertEqual(
            reply.status_code,
            401,msg=reply)

    def test_get_users_as_admin(self):
        tested_app = self.app.test_client()
        tested_app.set_app(self.app)

        tested_app.t_post('/login',data={"email":"admin@example.com", "password": "admin"})

        reply = tested_app.get('/users')
        html = reply.get_data(as_text=True)
        self.assertEqual(
            reply.status_code,
            200,msg=html)

    def test_zeta_all_registered(self):
        tested_app = self.app.test_client()
        tested_app.set_app(self.app)

        tested_app.t_post('/login',data={"email":"admin@example.com", "password": "admin"})

        reply = tested_app.get('/users')
        html = reply.get_data(as_text=True)
        self.assertEqual(
            reply.status_code,
            200,msg=html)

        for u in ["Admin Admin", "Tester OGF"]:
            self.assertIn(u,html,msg=html)


if __name__ == '__main__':
    unittest.main()