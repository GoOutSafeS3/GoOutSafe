import unittest
import json
from flask import request, jsonify
from monolith.app import create_app
from flask_test_with_csrf import FlaskClient
from utils import do_login, do_logout, send_registration_form, edit_restaurant, get_my_restaurant_id

class TestRegistration(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.app = create_app()
        self.app.test_client_class = FlaskClient

    def test_0(self):
        client = self.app.test_client()
        client.set_app(self.app)
        form = {
            "email":"testerGoodFormOperator@test.me",
            "firstname":"Tester",
            "lastname":"OGF",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"12345678901",
            "ssn": "",
        }

        rest = {
            "name":"Restaurant at the End of the Universe",
            "phone":"123456789001",
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
        do_logout(client)

        form = {
            "email":"testerGoodFormOperator2@test.me",
            "firstname":"Tester2",
            "lastname":"OGF2",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"123456789002",
            "ssn": ""
        }
        rest = {
            "name":"Restaurant at the End of the Pizza",
            "phone":"123456789102",
            "lat":"43.431481",
            "lon":"10.242915",
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

    def test_get_edit_id(self):
        client = self.app.test_client()
        client.set_app(self.app)

        do_login(client,"testerGoodFormOperator@test.me", "42")
        id = get_my_restaurant_id(client)
        self.assertIsNotNone(id)
        reply = client.t_get('/restaurants/'+str(id)+"/edit")
        self.assertEqual(reply.status_code, 200, msg=reply.get_data(as_text=True))

    def test_post_edit(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client,"testerGoodFormOperator@test.me", "42")
        id = get_my_restaurant_id(client)
        self.assertIsNotNone(id)
        form = {
            "name":"Restaurant at the End of the Universe",
            "phone":"123456789003",
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
        reply = edit_restaurant(client, id, form.copy())
        self.assertEqual(reply.status_code, 302, msg=reply.get_data(as_text=True))
        reply = client.t_get('/restaurants/'+str(id))
        self.assertEqual(reply.status_code, 200, msg=reply.get_data(as_text=True))
        for k,v in form.items():
            if k == "closed_days":
                if v == 1:
                    self.assertTrue("Monday" in reply.get_data(as_text=True), msg=v+"\n"+reply.get_data(as_text=True))
                if v == 2:
                    self.assertTrue("Tuesday" in reply.get_data(as_text=True), msg=v+"\n"+reply.get_data(as_text=True))
            else:
                self.assertTrue(v in reply.get_data(as_text=True), msg=v+"\n"+reply.get_data(as_text=True))

    def test_post_edit_only_dinner(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client,"testerGoodFormOperator@test.me", "42")
        id = get_my_restaurant_id(client)
        self.assertIsNotNone(id)
        form = {
            "name":"Restaurant at the End of the Universe",
            "phone":"123456789003",
            "lat":"43.431489",
            "lon":"10.242911",
            "first_opening_hour": None,
            "first_closing_hour": None,
            "second_opening_hour": "19",
            "second_closing_hour": "23",
            "occupation_time": "2",
            "closed_days": ["1","2"],
            "cuisine_type": "Pizzoria",
            "menu": "Napolitano"
        }
        reply = edit_restaurant(client, id, form.copy())
        self.assertEqual(reply.status_code, 302, msg=reply.get_data(as_text=True))

    def test_post_edit_only_lunch(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client,"testerGoodFormOperator@test.me", "42")
        id = get_my_restaurant_id(client)
        self.assertIsNotNone(id)
        form = {
            "name":"Restaurant at the End of the Universe",
            "phone":"123456789003",
            "lat":"43.431489",
            "lon":"10.242911",
            "first_opening_hour": "12",
            "first_closing_hour": "15",
            "second_opening_hour": None,
            "second_closing_hour": None,
            "occupation_time": "2",
            "closed_days": ["1","2"],
            "cuisine_type": "Pizzoria",
            "menu": "Napolitano"
        }
        reply = edit_restaurant(client, id, form.copy())
        self.assertEqual(reply.status_code, 302, msg=reply.get_data(as_text=True))

    def test_post_edit_wrong_user(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client,"testerGoodFormOperator2@test.me", "42")
        id = get_my_restaurant_id(client)
        self.assertIsNotNone(id)
        form = {
            "name":"Restaurant at the End of the Universe",
            "phone":"123456789004",
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
        reply = edit_restaurant(client, id-1, form.copy()) #id-1 because id is the restorant of operato2
        self.assertEqual(reply.status_code, 401, msg=reply.get_data(as_text=True))

    def test_post_edit_wrong_hours(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client,"testerGoodFormOperator@test.me", "42")
        id = get_my_restaurant_id(client)
        self.assertIsNotNone(id)
        form = {
            "name": "Restaurant at the End of the Universe",
            "phone":"123456789005",
            "lat":"43.431489",
            "lon":"10.242911",
            "first_opening_hour": "12",
            "first_closing_hour": "15",
            "second_opening_hour": "19",
            "second_closing_hour": "23",
            "occupation_time": "2",
            "closed_days": ["1","2"],
            "cuisine_type": "None",
            "menu": "None"
        }
        possibilities = [
            {
                "first_opening_hour": "12", 
                "first_closing_hour": "11", #wrong hours at lunch
                "second_opening_hour": "19",
                "second_closing_hour": "23",
            },
            {
                "first_opening_hour": "12", 
                "first_closing_hour": "15",
                "second_opening_hour": "19",
                "second_closing_hour": "18",
            },
            {
                "first_opening_hour": "12", 
                "first_closing_hour": "15",
                "second_opening_hour": "19",
                "second_closing_hour": "37",
            },
            {
                "first_opening_hour": "12", 
                "first_closing_hour": "20",
                "second_opening_hour": "19",
                "second_closing_hour": "22",
            },
            {
                "first_opening_hour": "20", 
                "first_closing_hour": "22",
                "second_opening_hour": "12",
                "second_closing_hour": "15",
            },
            {
                "first_opening_hour": None, 
                "first_closing_hour": None,
                "second_opening_hour": "23",
                "second_closing_hour": "19",
            },
            {
                "first_opening_hour": "15", 
                "first_closing_hour": "12",
                "second_opening_hour": None,
                "second_closing_hour": None,
            }]
        for pos in possibilities:
            dup = form.copy()
            for k,v in pos.items():
                dup[k] = v
            reply = edit_restaurant(client, id, dup)
            self.assertEqual(reply.status_code, 400, msg=str(pos)+reply.get_data(as_text=True))

    def test_post_edit_wrong_data(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client,"testerGoodFormOperator@test.me", "42")
        id = get_my_restaurant_id(client)
        self.assertIsNotNone(id)
        form = {
            "name":"Restaurant at the End of the Universe",
            "phone":"123456789003",
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
        for k,v in form.items():
            dup = form.copy()
            dup[k] = None
            reply = edit_restaurant(client, id, dup)
            self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))