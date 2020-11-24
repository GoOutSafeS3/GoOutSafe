import unittest
from monolith.app import create_app
from flask_test_with_csrf import FlaskClient
from flask import url_for
from flask_login import current_user
from utils import do_login, get_restaurant_id, get_tables_ids, send_registration_form
from random import randint

class TestTables(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.app = create_app()
        self.app.test_client_class = FlaskClient
    
    def start_operator(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "operator@example.com", "operator")
        rest_id = get_restaurant_id(client)
        self.assertIsNotNone(rest_id)
        ms= get_tables_ids(client, rest_id)
        tab_id = ms[0]
        return client, rest_id, ms, tab_id

    def start_operator2(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "operator2@example.com", "operator")
        return client

    def start_operator3(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "operator3@example.com", "operator")
        return client

    def test_list_tables(self):
        client, rest_id, ms, tab_id = self.start_operator()
        self.assertTrue(ms != [])
    
    def test_post_get_edit_table(self):
        client, rest_id, ms, tab_id = self.start_operator()
        num = randint(500,10000)
        reply = client.t_post("/tables/"+str(tab_id)+"/edit", data={"capacity": str(num)})
        self.assertEqual(reply.status_code, 302)
        reply = client.t_get("/restaurants/"+str(rest_id))
        self.assertIn(str(num), reply.get_data(as_text=True))
        reply = client.t_get("/tables/"+str(tab_id)+"/edit")
        self.assertIn(str(num), reply.get_data(as_text=True))

    def test_get_edit_table(self):
        client, rest_id, ms, tab_id = self.start_operator()
        reply = client.t_get("/tables/"+str(tab_id)+"/edit")
        self.assertEqual(reply.status_code, 200)

    def test_wrong_post_edit_table(self):
        client, rest_id, ms, tab_id = self.start_operator()
        reply = client.t_post("/tables/"+str(tab_id)+"/edit", data={"capacity": None})
        self.assertEqual(reply.status_code, 400)

    def test_zero_post_edit_table(self):
        client, rest_id, ms, tab_id = self.start_operator()
        reply = client.t_post("/tables/"+str(tab_id)+"/edit", data={"capacity": "0"})
        self.assertEqual(reply.status_code, 400)

    def test_wrong_user_edit_table(self):
        client, rest_id, ms, tab_id = self.start_operator()
        client2 = self.start_operator2()
        reply = client2.t_post("/tables/"+str(tab_id)+"/edit", data={"capacity": "6"})
        self.assertEqual(reply.status_code, 401)
    
    def test_post_add_table(self):
        client, rest_id, ms, tab_id = self.start_operator()
        num = randint(500,10000)
        reply = client.t_post("/tables/add", data={"capacity": str(num)})
        self.assertEqual(reply.status_code, 302)
        reply = client.t_get("/restaurants/"+str(rest_id))
        self.assertIn(str(num), reply.get_data(as_text=True))

    def test_get_add_table(self):
        client, rest_id, ms, tab_id = self.start_operator()
        reply = client.t_get("/tables/add")
        self.assertEqual(reply.status_code, 200)

    def test_wrong_post_add_table(self):
        client, rest_id, ms, tab_id = self.start_operator()
        reply = client.t_post("/tables/add", data={"capacity": None})
        self.assertEqual(reply.status_code, 400)

    def test_zero_post_add_table(self):
        client, rest_id, ms, tab_id = self.start_operator()
        reply = client.t_post("/tables/add", data={"capacity": "0"})
        self.assertEqual(reply.status_code, 400)

    def test_post_delete_table(self):
        client, rest_id, ms, tab_id = self.start_operator()
        tab_id = 7
        reply = client.t_get("/tables/%d/delete"%tab_id)
        self.assertEqual(reply.status_code, 302)
    
    def test_post_old_booking_delete_table(self):
        client = self.start_operator2()
        tab_id = 2
        reply = client.t_get("/tables/%d/delete"%tab_id)
        self.assertEqual(reply.status_code, 302)

    def test_wrong_user_delete_table(self):
        client, rest_id, ms, tab_id = self.start_operator()
        num = randint(500,10000)
        reply = client.t_post("/tables/add", data={"capacity": str(num)})
        reply = client.t_get("/restaurants/"+str(rest_id))
        client, rest_id, ms, tab_id = self.start_operator()
        tab_id = ms[-1]
        client2 = self.start_operator2()
        reply = client2.t_get("/tables/%d/delete"%tab_id)
        self.assertEqual(reply.status_code, 401, msg=str(ms))

    def test_booked_delete_table(self):
        client = self.start_operator3()
        tab_id = 4
        reply = client.t_get("/tables/%d/delete"%tab_id)
        self.assertEqual(reply.status_code, 409)