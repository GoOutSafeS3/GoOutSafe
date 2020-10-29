import unittest
from monolith.app import create_app_testing
from flask_test_with_csrf import FlaskClient
from flask import url_for
from flask_login import current_user
from monolith.classes.tests.utils import do_login, do_logout

class TestLogin(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.app = create_app_testing()
        self.app.test_client_class = FlaskClient

    def setup_app(self):
        self.app = create_app_testing()
        self.app.test_client_class = FlaskClient
        tested_app = self.app.test_client()
        tested_app.set_app(self.app)
        return tested_app

    def do_delete_operator(self,client, email, password):
        return client.t_post('/delete_operator',data={"email":email, "password": password})
    
    def do_delete_customer(self,client, email, password):
        return client.t_post('/delete_user',data={"email":email, "password": password})

    def test_delete_without_login(self):
        client = self.setup_app()
        reply = client.t_get('/delete_operator')
        self.assertEqual(reply.status_code, 401, msg=reply.get_data(as_text=True))

        reply = client.t_get('/delete_user')
        self.assertEqual(reply.status_code, 401, msg=reply.get_data(as_text=True))

    def test_delete_log_as_admin(self):
        client = self.setup_app()        
        do_login(client, "example@example.com","admin")

        reply = client.t_get('/delete_operator')
        self.assertEqual(reply.status_code, 401, msg=reply.get_data(as_text=True))

        reply = client.t_get('/delete_user')
        self.assertEqual(reply.status_code, 401, msg=reply.get_data(as_text=True))

    def test_delete_log_as_health_authority(self):
        client = self.setup_app()        
        do_login(client, "health@authority.com","health")
        
        reply = client.t_get('/delete_operator')
        self.assertEqual(reply.status_code, 401, msg=reply.get_data(as_text=True))

        reply = client.t_get('/delete_user')
        self.assertEqual(reply.status_code, 401, msg=reply.get_data(as_text=True))


    def test_delete_log_as_operator(self):
        client = self.setup_app()        
        do_login(client, "operator@example.com","operator")

        reply = client.t_get('/delete_user')
        self.assertEqual(reply.status_code, 401, msg=reply.get_data(as_text=True))

        reply = client.t_get('/delete_operator')
        self.assertEqual(reply.status_code, 200, msg=reply.get_data(as_text=True))

        reply = self.do_delete_operator(client, "operator@example.com","operator")
        self.assertEqual(reply.status_code, 204, msg=reply.get_data(as_text=True))

    def test_delete_log_as_customer(self):
        client = self.setup_app()        
        do_login(client, "customer@example.com","customer")

        reply = client.t_get('/delete_operator')
        self.assertEqual(reply.status_code, 401, msg=reply.get_data(as_text=True))

        reply = client.t_get('/delete_user')
        self.assertEqual(reply.status_code, 200, msg=reply.get_data(as_text=True))

        reply = self.do_delete_customer(client, "customer@example.com","customer")
        self.assertEqual(reply.status_code, 204, msg=reply.get_data(as_text=True))


    def test_delete_post_wrong_pass(self):
        client = self.setup_app()        
        do_login(client, "customer@example.com","customer")
        reply = self.do_delete_customer(client, "customer@example.com","the_customer")
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))
        do_logout(client)

        do_login(client, "operator@example.com","operator")
        reply = self.do_delete_operator(client, "operator@example.com","the_operator")
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))
        do_logout(client)


    def test_delete_post_wrong_mail(self):
        client = self.setup_app()        
        do_login(client, "customer@example.com","customer")
        reply = self.do_delete_customer(client, "the_customer@example.com","customer")
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))
        do_logout(client)

        do_login(client, "operator@example.com","operator")
        reply = self.do_delete_operator(client, "the_operator@example.com","operator")
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))
        do_logout(client)

    def test_delete_post_bad_pass(self):
        client = self.setup_app()        
        do_login(client, "customer@example.com","customer")
        reply = self.do_delete_customer(client, "customer@example.com",None)
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))
        do_logout(client)

        do_login(client, "operator@example.com","operator")
        reply = self.do_delete_operator(client, "operator@example.com",None)
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))
        do_logout(client)

    def test_delete_post_bad_mail(self):
        client = self.setup_app()        
        do_login(client, "customer@example.com","customer")
        reply = self.do_delete_customer(client, None,"customer")
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))
        do_logout(client)

        do_login(client, "operator@example.com","operator")
        reply = self.do_delete_operator(client, None, "operator")
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))
        do_logout(client)