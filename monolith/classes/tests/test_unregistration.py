import unittest
from monolith.app import create_app
from flask_test_with_csrf import FlaskClient
from flask import url_for
from flask_login import current_user
from monolith.classes.tests.utils import do_login, do_logout

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
        do_login(client, "example@example.com","admin")

        reply = client.t_get('/delete')
        self.assertEqual(reply.status_code, 401, msg=reply.get_data(as_text=True))

    def test_delete_log_as_health_authority(self):
        client = self.setup_app()        
        do_login(client, "health@authority.com","health")
        
        reply = client.t_get('/delete')
        self.assertEqual(reply.status_code, 401, msg=reply.get_data(as_text=True))


    def test_delete_log_as_operator(self):
        client = self.setup_app()        
        do_login(client, "operator@example.com","operator")

        reply = client.t_get('/delete')
        self.assertEqual(reply.status_code, 200, msg=reply.get_data(as_text=True))

        form = {
            'email': "operator@example.com",
            'password': "operator"
        }
        reply = client.t_post('/delete', data=form)
        self.assertEqual(reply.status_code, 302, msg=reply.get_data(as_text=True))

        do_login(client, "example@example.com", "admin")
        
        reply = client.t_get('/restaurants')
        self.assertNotIn("Trial Restaurant", reply.get_data(as_text=True), msg=reply.get_data(as_text=True))

        reply = client.t_get('/users')
        self.assertNotIn("Operator Operator", reply.get_data(as_text=True), msg=reply.get_data(as_text=True))
        
        do_logout(client)


        reply = do_login(client, "operator@example.com","operator")
        self.assertEqual(reply.status_code, 401)

    def test_delete_log_as_customer(self):
        client = self.setup_app()        
        do_login(client, "customer@example.com","customer")

        reply = client.t_get('/delete')
        self.assertEqual(reply.status_code, 200, msg=reply.get_data(as_text=True))

        form = {
            "email": "customer@example.com",
            "password": "customer"
        }
        reply = client.t_post('/delete', data=form)
        self.assertEqual(reply.status_code, 302, msg=reply.get_data(as_text=True))
        reply = client.t_get('/')
        self.assertIn("success",reply.get_data(as_text=True),  msg=reply.get_data(as_text=True))

        do_login(client, "example@example.com", "admin")
        reply = client.t_get('/users')
        self.assertNotIn("Customer Customer", reply.get_data(as_text=True), msg=reply.get_data(as_text=True))
        do_logout(client)

        reply = do_login(client, "customer@example.com","customer")
        self.assertEqual(reply.status_code, 401)


    def test_delete_log_as_positive_customer(self):
        client = self.setup_app()        
        do_login(client, "positive@example.com","positive")

        reply = self.do_delete(client, "positive@example.com","positive")
        self.assertEqual(reply.status_code, 302, msg=reply.get_data(as_text=True))
        reply = client.t_get('/')
        self.assertIn("You cannot delete your data as long as you are positive",reply.get_data(as_text=True),  msg=reply.get_data(as_text=True))


    def test_delete_post_wrong_pass(self):
        client = self.setup_app()        
        do_login(client, "customer@example.com","customer")
        reply = self.do_delete(client, "customer@example.com","the_customer")
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))
        do_logout(client)

    def test_delete_post_wrong_mail(self):
        client = self.setup_app()        
        do_login(client, "customer@example.com","customer")
        reply = self.do_delete(client, "the_customer@example.com","customer")
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))
        do_logout(client)

    def test_delete_post_bad_pass(self):
        client = self.setup_app()        
        do_login(client, "customer@example.com","customer")
        reply = self.do_delete(client, "customer@example.com",None)
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))
        do_logout(client)

    def test_delete_post_bad_mail(self):
        client = self.setup_app()        
        do_login(client, "customer@example.com","customer")
        reply = self.do_delete(client, None,"customer")
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))
        do_logout(client)