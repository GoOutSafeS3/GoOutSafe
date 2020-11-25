import unittest
from monolith.app import create_app
from flask_test_with_csrf import FlaskClient
from monolith.classes.tests.utils import do_login, do_logout


class TestEdit(unittest.TestCase):
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

    def test_error401(self):
        client = self.app.test_client()
        client.set_app(self.app)
        reply = client.t_get('/edit')
        self.assertEqual(reply.status_code, 401, msg=reply.get_data(as_text=True))
        do_login(client, "admin@example.com", "admin")
        reply = client.t_get('/edit')
        self.assertEqual(reply.status_code, 401, msg=reply.get_data(as_text=True))
        do_logout(client)
        do_login(client, "admin@example.com", "health")
        reply = client.t_get('/edit')
        self.assertEqual(reply.status_code, 401, msg=reply.get_data(as_text=True))

    def test_get_customer200(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "gianni@example.com", "gianni")
        reply = client.t_get('/edit')
        self.assertEqual(reply.status_code, 200)

    def test_get_operator200(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "operator@example.com", "operator")
        reply = client.t_get('/edit')
        self.assertEqual(reply.status_code, 200)

    def test_password400(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "gianni@example.com", "gianni")
        reply = client.t_get('/edit')
        self.assertEqual(reply.status_code, 200)
        form = {
            "firstname": "Anna",
            "old_password": "errata"
        }
        reply = client.t_post('/edit', data=form)
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))

    def test_dateerror400(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "gianni@example.com", "gianni")
        reply = client.t_get('/edit')
        self.assertEqual(reply.status_code, 200)
        form = {
            "dateofbirth":"11/11/2030",
            "old_password": "gianni"
        }
        reply = client.t_post('/edit', data=form)
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))

    def test_telephone_exist400(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "gianni@example.com", "gianni")
        reply = client.t_get('/edit')
        self.assertEqual(reply.status_code, 200)
        form = {
            "telephone": "2354673561",
            "old_password": "gianni"
        }
        reply = client.t_post('/edit', data=form)
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))

    def test_password_repeat400(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "gianni@example.com", "gianni")
        reply = client.t_get('/edit')
        self.assertEqual(reply.status_code, 200)
        form = {
            "new_password":"ciao",
            "password_repeat":"ciao421",
            "old_password": "gianni"
        }
        reply = client.t_post('/edit', data=form)
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))

    def test_insert_old_password400(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "gianni@example.com", "gianni")
        reply = client.t_get('/edit')
        self.assertEqual(reply.status_code, 200)
        form = {
            "old_password": ""
        }
        reply = client.t_post('/edit', data=form)
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))

    def test_correct_edit(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "alice@example.com", "alice")
        reply = client.t_get('/edit')
        self.assertEqual(reply.status_code, 200)
        form = {
            "old_password": "alice",
            "firstname":"Alice Beatrice",
            "lastname":"alice",
            "new_password":"pass12",
            "password_repeat":"pass12",
            "email":"alice@example.com",
            "dateofbirth":"01/01/1970",
            "telephone":"12345678900",
        }
        reply = client.t_post('/edit', data=form)
        self.assertEqual(reply.status_code, 302, msg=reply.get_data(as_text=True))

    def test_existing_ssn400(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "operator@example.com", "operator")
        form = {
            "firstname": "Operator",
            "lastname": "Operator",
            "ssn": "1234567890",
            "password": "operator",
        }
        reply = client.t_post('/edit', data=form)
        self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))

