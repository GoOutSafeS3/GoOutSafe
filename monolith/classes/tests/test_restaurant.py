import unittest
from monolith.app import create_app
from flask_test_with_csrf import FlaskClient
from flask import url_for
from flask_login import current_user
from utils import do_login, do_logout
import datetime

class TestRestaurant(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.app = create_app()
        self.app.test_client_class = FlaskClient

    def test_restaurant_list(self):
        client = self.app.test_client()
        client.set_app(self.app)
        reply = client.t_get("/restaurants")
        self.assertEqual(reply.status_code, 200)
        reply_data = reply.get_data(as_text = True)
        with self.app.test_request_context():
            self.assertTrue("Rest 1" in reply_data)
            self.assertIn("/restaurant/1", reply_data)

    def test_restaurants_map(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "anna@example.com", "anna")
        reply = client.t_get("/restaurants_map")
        do_logout(client)
        self.assertEqual(reply.status_code, 200, msg=reply.get_data(as_text = True))

    def test_restaurants_map_notcustomer(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "admin@example.com", "admin")
        reply = client.t_get("/restaurants_map")
        self.assertEqual(reply.status_code, 401, msg=reply.get_data(as_text = True))
        do_logout(client)

    def test_profile_has_name(self):
        client = self.app.test_client()
        client.set_app(self.app)
        reply = client.t_get("/restaurants/4")
        self.assertEqual(reply.status_code, 200)
        reply_data = reply.get_data(as_text = True)
        with self.app.test_request_context():
            self.assertTrue("Rest 4" in reply_data)

    def test_profile_has_phone(self):
        client = self.app.test_client()
        client.set_app(self.app)
        reply = client.t_get("/restaurants/4")
        self.assertEqual(reply.status_code, 200)
        reply_data = reply.get_data(as_text = True)
        with self.app.test_request_context():
            self.assertTrue("050123456" in reply_data)

    def test_profile_has_opening_hours(self):
        client = self.app.test_client()
        client.set_app(self.app)
        reply = client.t_get("/restaurants/4")
        self.assertEqual(reply.status_code, 200)
        reply_data = reply.get_data(as_text = True)
        with self.app.test_request_context():
            self.assertTrue("10:00" in reply_data)
            self.assertTrue("12:00" in reply_data)
            self.assertTrue("20:00" in reply_data)
            self.assertTrue("23:00" in reply_data)

    def test_profile_has_closed_days(self):
        client = self.app.test_client()
        client.set_app(self.app)
        reply = client.t_get("/restaurants/4")
        self.assertEqual(reply.status_code, 200)
        reply_data = reply.get_data(as_text = True)
        with self.app.test_request_context():
            self.assertTrue("Monday" in reply_data)
            self.assertTrue("Sunday" in reply_data)
            self.assertFalse("Tuesday" in reply_data)
            self.assertFalse("Wednesday" in reply_data)
            self.assertFalse("Thursday" in reply_data)
            self.assertFalse("Friday" in reply_data)
            self.assertFalse("Saturday" in reply_data)

    def test_profile_has_cuisine_type(self):
        client = self.app.test_client()
        client.set_app(self.app)
        reply = client.t_get("/restaurants/4")
        self.assertEqual(reply.status_code, 200)
        reply_data = reply.get_data(as_text = True)
        with self.app.test_request_context():
            self.assertIn("True Italian Restaurant", reply_data)

    def test_profile_has_menu(self):
        client = self.app.test_client()
        client.set_app(self.app)
        reply = client.t_get("/restaurants/4")
        self.assertEqual(reply.status_code, 200)
        reply_data = reply.get_data(as_text = True)
        with self.app.test_request_context():
            self.assertIn("Pizza", reply_data)
            self.assertIn("Pasta Bolognese", reply_data)
            self.assertIn("Breadsticks", reply_data)

    def test_bad_form_search(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "anna@example.com","anna")
        reply = client.t_get("/restaurants/search")
        self.assertEqual(reply.status_code, 200)

        form = {
            "name":"",
            "menu":"",
            "cuisine_type":"",
            "open_day":"",
            "opening_time":""
        }

        reply = client.t_post("/restaurants/search",data=form)
        do_logout(client)
        self.assertEqual(reply.status_code, 400)

    def test_empty_form_search(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "anna@example.com","anna")
        reply = client.t_get("/restaurants/search")
        self.assertEqual(reply.status_code, 200)

        form = {
            "name":"",
            "menu":"",
            "cuisine_type":"",
            "open_day":"0",
            "opening_time":"Not Specified"
        }

        reply = client.t_post("/restaurants/search",data=form)
        do_logout(client)
        reply_data = reply.get_data(as_text = True)
        self.assertEqual(reply.status_code, 200, msg=reply_data)
        self.assertIn("Rest 1", reply_data, msg=reply_data)


    def test_good_form_search(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "anna@example.com","anna")
        reply = client.t_get("/restaurants/search")
        self.assertEqual(reply.status_code, 200)

        form = {
            "name":"Rest",
            "menu":"",
            "cuisine_type":"",
            "open_day":"0",
            "opening_time":"Not Specified"
        }

        reply = client.t_post("/restaurants/search",data=form)
        do_logout(client)
        reply_data = reply.get_data(as_text = True)
        self.assertEqual(reply.status_code, 200, msg=reply_data)
        self.assertIn("Rest 4", reply_data, msg=reply_data)

    def test_goood_form_empty_search(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "anna@example.com","anna")
        reply = client.t_get("/restaurants/search")
        self.assertEqual(reply.status_code, 200)

        form = {
            "name":"NotExist",
            "menu":"",
            "cuisine_type":"",
            "open_day":"0",
            "opening_time":"Not Specified"
        }

        reply = client.t_post("/restaurants/search",data=form)
        do_logout(client)
        reply_data = reply.get_data(as_text = True)
        self.assertEqual(reply.status_code, 404, msg=reply_data)

    def test_goood_form_multi_search(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "anna@example.com","anna")
        reply = client.t_get("/restaurants/search")
        self.assertEqual(reply.status_code, 200)

        form = {
            "name":"t",
            "menu":"",
            "cuisine_type":"italian",
            "open_day":"2",
            "opening_time":"21"
        }

        reply = client.t_post("/restaurants/search",data=form)
        do_logout(client)
        reply_data = reply.get_data(as_text = True)
        self.assertEqual(reply.status_code, 200, msg=reply_data)
        self.assertIn("Rest 4", reply_data, msg=reply_data)

    def test_goood_form_bad_time_search(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "anna@example.com","anna")
        reply = client.t_get("/restaurants/search")
        self.assertEqual(reply.status_code, 200)

        form = {
            "name":"t",
            "menu":"italian",
            "cuisine_type":"",
            "open_day":"2",
            "opening_time":"5"
        }

        reply = client.t_post("/restaurants/search",data=form)
        do_logout(client)
        reply_data = reply.get_data(as_text = True)
        self.assertEqual(reply.status_code, 404, msg=reply_data)

    def test_overview_needs_operator(self):
        client = self.app.test_client()
        client.set_app(self.app)
        reply = client.t_get("/restaurants/1/overview")
        self.assertEqual(reply.status_code, 401)
        
        reply = client.t_get("/restaurants/1/overview/2020/10/10")
        self.assertEqual(reply.status_code, 401)

    def test_overview_slots(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "operator4@example.com","operator")
        reply = client.t_get("/restaurants/4/overview/2020/10/5")
        reply_data = reply.get_data(as_text = True)
        self.assertIn("First opening:", reply_data)
        self.assertIn("Second opening:", reply_data)

        today = datetime.datetime.today()
        reply = client.t_get(f"/restaurants/4/overview/{today.year}/{today.month}/{today.day}")
        reply_data = reply.get_data(as_text = True)
        self.assertIn("First opening:", reply_data)
        self.assertNotIn("Second opening:", reply_data)

        today = datetime.datetime.today()
        reply = client.t_get(f"/restaurants/4/overview/2020/10/3")
        reply_data = reply.get_data(as_text = True)
        self.assertNotIn("First opening:", reply_data)
        self.assertIn("Second opening:", reply_data)

    def test_overview_wrong_operator(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "operator2@example.com","operator2")

        reply = client.t_get("/restaurants/1/overview")
        self.assertEqual(reply.status_code, 401)
        
        reply = client.t_get("/restaurants/1/overview/2020/10/10")
        self.assertEqual(reply.status_code, 401)

    def test_overview_invalid_range(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "operator4@example.com","operator")

        data={
            "from_h":"foo",
            "from_m":"foo",
            "to_h":"foo",
            "to_m":"foo"
        }
        
        reply = client.t_get("/restaurants/4/overview/2020/10/5", query_string=data)
        self.assertEqual(reply.status_code, 400)

        data={
            "from_h":"11",
            "from_m":"00",
            "to_h":"10",
            "to_m":"00"
        }
        
        reply = client.t_get("/restaurants/4/overview/2020/10/5", query_string=data)
        self.assertEqual(reply.status_code, 400)

        data={
            "from_h":"27",
            "from_m":"00",
            "to_h":"28",
            "to_m":"00"
        }
        
        reply = client.t_get("/restaurants/4/overview/2020/10/5", query_string=data)
        self.assertEqual(reply.status_code, 400)

    def test_overview_range(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "operator4@example.com","operator")

        data={
            "from_h":"20",
            "from_m":"00",
            "to_h":"22",
            "to_m":"00"
        }
        
        reply = client.t_get("/restaurants/4/overview/2020/10/5", query_string=data)
        reply_data = reply.get_data(as_text=True)

        self.assertIn("No. people total: 5", reply_data) # TODO Change with actual data
