import unittest
import json
from flask import request, jsonify
from monolith.app import create_app
from flask_test_with_csrf import FlaskClient
from utils import do_login, send_registration_form, edit_restaurant, get_my_restaurant_id

class TestRegistration(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.app = create_app()
        self.app.test_client_class = FlaskClient

        tested_app = self.app.test_client()
        tested_app.set_app(self.app)

        form = {
            "email":"testerGoodFormOperator@test.me",
            "firstname":"Tester",
            "lastname":"OGF",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"123456789001",
            "restaurant_name":"Restaurant at the End of the Universe",
            "restaurant_phone":"123456789001",
            "restaurant_latitude":"43.431489",
            "restaurant_longitude":"10.242911",
        }
        send_registration_form(tested_app, '/create_operator', form)

        form = {
            "email":"testerGoodFormOperator2@test.me",
            "firstname":"Tester2",
            "lastname":"OGF2",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"123456789002",
            "restaurant_name":"Restaurant at the End of the Pizza",
            "restaurant_phone":"123456789100",
            "restaurant_latitude":"43.431481",
            "restaurant_longitude":"10.242915",
        }
        send_registration_form(tested_app, '/create_operator', form)


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
            "opening_hour_lunch": "13",
            "closing_hour_lunch": "15",
            "opening_hour_dinner": "19",
            "closing_hour_dinner": "23",
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
            "opening_hour_lunch": None,
            "closing_hour_lunch": None,
            "opening_hour_dinner": "19",
            "closing_hour_dinner": "23",
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
            "opening_hour_lunch": "12",
            "closing_hour_lunch": "15",
            "opening_hour_dinner": None,
            "closing_hour_dinner": None,
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
            "opening_hour_lunch": "13",
            "closing_hour_lunch": "15",
            "opening_hour_dinner": "19",
            "closing_hour_dinner": "23",
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
            "opening_hour_lunch": "12",
            "closing_hour_lunch": "15",
            "opening_hour_dinner": "19",
            "closing_hour_dinner": "23",
            "occupation_time": "2",
            "closed_days": ["1","2"],
            "cuisine_type": "None",
            "menu": "None"
        }
        possibilities = [
            {
                "opening_hour_lunch": "12", 
                "closing_hour_lunch": "11", #wrong hours at lunch
                "opening_hour_dinner": "19",
                "closing_hour_dinner": "23",
            },
            {
                "opening_hour_lunch": "12", 
                "closing_hour_lunch": "15",
                "opening_hour_dinner": "19",
                "closing_hour_dinner": "18",
            },
            {
                "opening_hour_lunch": "12", 
                "closing_hour_lunch": "15",
                "opening_hour_dinner": "19",
                "closing_hour_dinner": "37",
            },
            {
                "opening_hour_lunch": "12", 
                "closing_hour_lunch": "20",
                "opening_hour_dinner": "19",
                "closing_hour_dinner": "22",
            },
            {
                "opening_hour_lunch": "20", 
                "closing_hour_lunch": "22",
                "opening_hour_dinner": "12",
                "closing_hour_dinner": "15",
            },
            {
                "opening_hour_lunch": None, 
                "closing_hour_lunch": None,
                "opening_hour_dinner": "23",
                "closing_hour_dinner": "19",
            },
            {
                "opening_hour_lunch": "15", 
                "closing_hour_lunch": "12",
                "opening_hour_dinner": None,
                "closing_hour_dinner": None,
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
            "opening_hour_lunch": "13",
            "closing_hour_lunch": "15",
            "opening_hour_dinner": "19",
            "closing_hour_dinner": "23",
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