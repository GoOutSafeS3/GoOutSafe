import unittest
from monolith.app import create_app
from flask_test_with_csrf import FlaskClient
from flask import url_for
from flask_login import current_user
from monolith.classes.tests.utils import do_login, do_logout, send_registration_form

class TestUnregistration(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.app = create_app()
        self.app.test_client_class = FlaskClient

    def setup_app(self):
        self.app = create_app()
        self.app.test_client_class = FlaskClient
        tested_app = self.app.test_client()
        tested_app.set_app(self.app)
        return tested_app
    
    def do_delete(self,client, email, password):
        return client.t_post('/delete',data={"email":email, "password": password})

    def test_delete_without_login(self):
        client = self.setup_app()
        reply = client.t_get('/delete')
        self.assertEqual(reply.status_code, 401, msg=reply.get_data(as_text=True))

    def test_delete_log_as_admin(self):
        client = self.setup_app()        
        do_login(client, "admin@example.com","admin")

        reply = client.t_get('/delete')
        self.assertEqual(reply.status_code, 401, msg=reply.get_data(as_text=True))

    def test_delete_log_as_health_authority(self):
        client = self.setup_app()        
        do_login(client, "health@example.com","health")
        
        reply = client.t_get('/delete')
        self.assertEqual(reply.status_code, 401, msg=reply.get_data(as_text=True))


    def test_delete_log_as_operator(self):
        client = self.setup_app()        
        form = {
            "email":"delete-operator@test.me",
            "firstname":"Operator",
            "lastname":"delete",
            "password":"operator",
            "password_repeat":"operator",
            "dateofbirth":"01/01/1970",
            "telephone":"12345671234",
            "ssn": "",
        }

        rest = {
            "name":"deleted restaurant",
            "phone":"12345671234",
            "lat":"43.431489",
            "lon":"10.242911",
            "first_opening_hour": "13",
            "first_closing_hour": "15",
            "second_opening_hour": "19",
            "second_closing_hour": "23",
            "occupation_time": "2",
            "closed_days": ["1","2"],
            "cuisine_type": "Pizzoria",
            "menu": "Napolitano"
        }
        reply = send_registration_form(client, '/create_operator', form)
        self.assertEqual(
            reply["status_code"],
            302, msg = reply["html"])
        reply = client.t_get('/')
        reply = send_registration_form(client, '/create_restaurant', rest)
        self.assertEqual(
            reply["status_code"],
            302, msg = reply["html"])

        reply = client.t_get('/delete')
        self.assertEqual(reply.status_code, 200, msg=reply.get_data(as_text=True))

        form = {
            'email': "delete-operator@test.me",
            'password': "operator"
        }
        reply = client.t_post('/delete', data=form)
        self.assertEqual(reply.status_code, 302, msg=reply.get_data(as_text=True))

        do_login(client, "admin@example.com", "admin")
        
        reply = client.t_get('/restaurants')
        self.assertNotIn("deleted restaurant", reply.get_data(as_text=True), msg=reply.get_data(as_text=True))

        reply = client.t_get('/users')
        self.assertNotIn("Operator delete", reply.get_data(as_text=True), msg=reply.get_data(as_text=True))
        
        do_logout(client)


        reply = do_login(client, "delete-operator@test.me","operator")
        self.assertEqual(reply.status_code, 401)

    def test_delete_log_as_customer(self):
        client = self.setup_app()
        
        form = {
            "email":"delete-user@test.me",
            "firstname":"asjdn",
            "lastname":"asjdn",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"01234567890",
            "ssn":""
        }

        reply = send_registration_form(client, '/create_user', form)
        
        self.assertEqual(
            reply["status_code"],
            302,msg=reply)        
        do_login(client, "delete-user@test.me","42")

        reply = client.t_get('/delete')
        self.assertEqual(reply.status_code, 200, msg=reply.get_data(as_text=True))

        form = {
            "email": form["email"],
            "password": form["password"]
        }
        reply = client.t_post('/delete', data=form)
        self.assertEqual(reply.status_code, 302, msg=reply.get_data(as_text=True))
        reply = client.t_get('/')
        self.assertIn("success",reply.get_data(as_text=True),  msg=reply.get_data(as_text=True))

        do_login(client, "admin@example.com", "admin")
        reply = client.t_get('/users')
        self.assertNotIn("asjdn asjdn", reply.get_data(as_text=True), msg=reply.get_data(as_text=True))
        do_logout(client)

        reply = do_login(client, "delete-user@test.me","42")
        self.assertEqual(reply.status_code, 401)


    def test_delete_log_as_positive_customer(self):
        client = self.setup_app()        
        do_login(client, "alice@example.com","alice")

        reply = self.do_delete(client, "alice@example.com","alice")
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))
        self.assertIn("You cannot delete your data as long as you are positive",reply.get_data(as_text=True),  msg=reply.get_data(as_text=True))


    def test_delete_post_wrong_pass(self):
        client = self.setup_app()        
        do_login(client, "gianni@example.com","gianni")
        reply = self.do_delete(client, "gianni@example.com","the_customer")
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))
        do_logout(client)

    def test_delete_post_wrong_mail(self):
        client = self.setup_app()        
        form = {
            "email":"delete-user@test.me",
            "firstname":"asjdn",
            "lastname":"asjdn",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"01234567890",
            "ssn":""
        }

        reply = send_registration_form(client, '/create_user', form)
        
        self.assertEqual(
            reply["status_code"],
            302,msg=reply)        
        do_login(client, "delete-user@test.me","42")

        reply = client.t_get('/delete')
        self.assertEqual(reply.status_code, 200, msg=reply.get_data(as_text=True))
        reply = self.do_delete(client, "the_customer@example.com","42")
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))
        do_logout(client)

    def test_delete_post_bad_pass(self):
        client = self.setup_app()        
        do_login(client, "gianni@example.com","gianni")
        reply = self.do_delete(client, "gianni@example.com",None)
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))
        do_logout(client)

    def test_delete_post_bad_mail(self):
        client = self.setup_app()        
        do_login(client, "gianni@example.com","gianni")
        reply = self.do_delete(client, None,"gianni")
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))
        do_logout(client)