import unittest
from flask import request, jsonify
from monolith.app import create_app
from flask_test_with_csrf import FlaskClient
from monolith.classes.tests.utils import do_login, do_logout

class TestRegistration(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.app = create_app("TEST")
        self.app.test_client_class = FlaskClient

    def setup_app(self):
        self.app = create_app("TEST")
        self.app.test_client_class = FlaskClient
        tested_app = self.app.test_client()
        tested_app.set_app(self.app)
        return tested_app

    def test_edit_without_login(self):
        client = self.app.test_client()
        client.set_app(self.app)
        reply = client.t_get('/edit')
        self.assertEqual(reply.status_code, 401, msg=reply.get_data(as_text=True))

    def test_edit_log_as_admin(self):
        client = self.app.test_client()
        client.set_app(self.app)       
        do_login(client, "example@example.com","admin")

        reply = client.t_get('/edit')
        self.assertEqual(reply.status_code, 401, msg=reply.get_data(as_text=True))

    def test_edit_log_as_health_authority(self):
        client = self.app.test_client()
        client.set_app(self.app)        
        do_login(client, "health@authority.com","health")
        
        reply = client.t_get('/edit')
        self.assertEqual(reply.status_code, 401, msg=reply.get_data(as_text=True))

    def test_get_edit(self):
        client = self.app.test_client()
        client.set_app(self.app)         
        do_login(client, "operator@example.com","operator")

        reply = client.t_get('/edit')
        self.assertEqual(reply.status_code, 200, msg=reply.get_data(as_text=True))
        
        do_logout(client)

        do_login(client, "customer@example.com","customer")

        reply = client.t_get('/edit')
        self.assertEqual(reply.status_code, 200, msg=reply.get_data(as_text=True))
        
        do_logout(client)

    def test_get_edit_no_change_form(self):
        client = self.app.test_client()
        client.set_app(self.app)         
        do_login(client, "operator@example.com","operator")

        form =  {
            "email":"operator@example.com",
            "firstname":"Operator",
            "lastname":"Operator",
            "dateofbirth":"05/10/2020",
            "telephone":"5551234563",
            "ssn":"",
            "password":"operator",
            "password_repeat":"operator"
        }

        reply = client.t_post('/edit',data=form)
        self.assertEqual(reply.status_code, 302, msg=reply.get_data(as_text=True))
        
        do_logout(client)


    def test_get_edit_bad_form(self):
        client = self.app.test_client()
        client.set_app(self.app)         
        do_login(client, "operator@example.com","operator")

        form =  {
            "email":"",
            "firstname":"Operator",
            "lastname":"Operator",
            "dateofbirth":"05/10/2020",
            "telephone":"123",
            "ssn":"",
            "password":"operator",
            "password_repeat":"operator"
        }

        reply = client.t_post('/edit',data=form)
        self.assertEqual(reply.status_code, 200, msg=reply.get_data(as_text=True))
        self.assertIn("This field is required.", reply.get_data(as_text=True), msg=reply.get_data(as_text=True))

    def test_get_edit_wrong_passw_form(self):
        client = self.app.test_client()
        client.set_app(self.app)         
        do_login(client, "operator@example.com","operator")

        form =  {
            "email":"operator@example.com",
            "firstname":"Operator",
            "lastname":"Operator",
            "dateofbirth":"05/10/2020",
            "telephone":"123",
            "ssn":"",
            "password":"the_operator",
            "password_repeat":"_operator"
        }

        reply = client.t_post('/edit',data=form)
        self.assertEqual(reply.status_code, 200, msg=reply.get_data(as_text=True))
        self.assertIn("Passwords do not match", reply.get_data(as_text=True), msg=reply.get_data(as_text=True))
        
        do_logout(client)

    def test_get_existing_mail_form(self):
        client = self.app.test_client()
        client.set_app(self.app)         
        do_login(client, "operator@example.com","operator")

        form =  {
            "email":"example@example.com",
            "firstname":"Operator",
            "lastname":"Operator",
            "dateofbirth":"05/10/2020",
            "telephone":"123",
            "ssn":"",
            "password":"operator",
            "password_repeat":"operator"
        }

        reply = client.t_post('/edit',data=form)
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))
        
        do_logout(client)

    def test_get_existing_telephone_form(self):
        client = self.app.test_client()
        client.set_app(self.app)         
        do_login(client, "operator@example.com","operator")

        form =  {
            "email":"exampleee@example.com",
            "firstname":"Operator",
            "lastname":"Operator",
            "dateofbirth":"05/10/2020",
            "telephone":"1234567890",
            "ssn":"",
            "password":"operator",
            "password_repeat":"operator"
        }

        reply = client.t_post('/edit',data=form)
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))
        
        do_logout(client)

    def test_get_existing_ssn_form(self):
        client = self.app.test_client()
        client.set_app(self.app)         
        do_login(client, "operator@example.com","operator")

        form =  {
            "email":"exampleee@example.com",
            "firstname":"Operator",
            "lastname":"Operator",
            "dateofbirth":"05/10/2020",
            "telephone":"12345678900000",
            "ssn":"1234567890",
            "password":"operator",
            "password_repeat":"operator"
        }

        reply = client.t_post('/edit',data=form)
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))
        
        do_logout(client)


    def test_get_edit_change_all_form_operator(self):
        client = self.setup_app()     
        do_login(client, "operator@example.com","operator")

        form =  {
            "email":"the_operator@example.com",
            "firstname":"Agent",
            "lastname":"Agent",
            "dateofbirth":"10/05/2002",
            "telephone":"555123456342",
            "ssn":"567",
            "password":"the_operator",
            "password_repeat":"the_operator"
        }

        reply = client.t_post('/edit',data=form)
        self.assertEqual(reply.status_code, 302, msg=reply.get_data(as_text=True))
        
        do_logout(client)

        reply = do_login(client, "operator@example.com","operator")
        self.assertEqual(reply.status_code, 401, msg=reply.get_data(as_text=True))
        reply = do_login(client, "the_operator@example.com","the_operator")
        reply_data = reply.get_data(as_text=True)
        self.assertEqual(reply.status_code, 302, msg=reply_data)
        reply = client.t_get('/')
        reply_data = reply.get_data(as_text=True)
        self.assertIn("Agent", reply_data, msg=reply_data)

    def test_get_edit_change_all_form_user(self):
        client = self.setup_app()       
        do_login(client, "customer@example.com","customer")

        form =  {
            "email":"the_customer@example.com",
            "firstname":"Agent",
            "lastname":"Agent",
            "dateofbirth":"10/05/2002",
            "telephone":"5551234563421",
            "ssn":"123",
            "password":"the_customer",
            "password_repeat":"the_customer"
        }

        reply = client.t_post('/edit',data=form)
        self.assertEqual(reply.status_code, 302, msg=reply.get_data(as_text=True))
        
        do_logout(client)

        reply = do_login(client, "customer@example.com","customer")
        self.assertEqual(reply.status_code, 401, msg=reply.get_data(as_text=True))
        reply = do_login(client, "the_customer@example.com","the_customer")
        reply_data = reply.get_data(as_text=True)
        self.assertEqual(reply.status_code, 302, msg=reply_data)
        reply = client.t_get('/')
        reply_data = reply.get_data(as_text=True)
        self.assertIn("Agent", reply_data, msg=reply_data)

if __name__ == '__main__':
    unittest.main()