import unittest
from monolith.app import create_app_testing
from flask_test_with_csrf import FlaskClient
from flask import url_for
from flask_login import current_user

app = create_app_testing()
app.test_client_class = FlaskClient
app.config['TESTING'] = True

class TestRestaurant(unittest.TestCase):
    def do_login(self,client, email, password):
        return client.t_post('/login',data={"email":email, "password": password})

    def test_restaurant_list(self):
        client = app.test_client()
        client.set_app(app)
        reply = client.t_get("/restaurants")
        self.assertEqual(reply.status_code, 200)
        reply_data = reply.get_data(as_text = True)
        with app.test_request_context():
            self.assertTrue("Trial Restaurant" in reply_data)

    def test_profile_has_name(self):
        client = app.test_client()
        client.set_app(app)
        reply = client.t_get("/restaurants/1")
        self.assertEqual(reply.status_code, 200)
        reply_data = reply.get_data(as_text = True)
        with app.test_request_context():
            self.assertTrue("Trial Restaurant" in reply_data)

    def test_profile_has_phone(self):
        client = app.test_client()
        client.set_app(app)
        reply = client.t_get("/restaurants/1")
        self.assertEqual(reply.status_code, 200)
        reply_data = reply.get_data(as_text = True)
        with app.test_request_context():
            self.assertTrue("555123456" in reply_data)

    def test_profile_has_opening_hours(self):
        client = app.test_client()
        client.set_app(app)
        reply = client.t_get("/restaurants/1")
        self.assertEqual(reply.status_code, 200)
        reply_data = reply.get_data(as_text = True)
        with app.test_request_context():
            self.assertTrue("10:00" in reply_data)
            self.assertTrue("16:00" in reply_data)
            self.assertTrue("23:00" in reply_data)

    def test_profile_has_closed_days(self):
        client = app.test_client()
        client.set_app(app)
        reply = client.t_get("/restaurants/1")
        self.assertEqual(reply.status_code, 200)
        reply_data = reply.get_data(as_text = True)
        with app.test_request_context():
            self.assertTrue("Monday" in reply_data)
            self.assertTrue("Sunday" in reply_data)
            self.assertFalse("Tuesday" in reply_data)
            self.assertFalse("Wednesday" in reply_data)
            self.assertFalse("Thursday" in reply_data)
            self.assertFalse("Friday" in reply_data)
            self.assertFalse("Saturday" in reply_data)

    def test_can_like_once(self):
        with app.test_client() as client:
            client.set_app(app)
            reply = self.do_login(client, "example@example.com", "admin")
            
            reply = client.t_get("/restaurants/like/1")
            reply_data = reply.get_data(as_text = True)
            self.assertFalse("already liked" in reply_data)
            
            reply = client.t_get("/restaurants/like/1")
            reply_data = reply.get_data(as_text = True)
            self.assertTrue("already liked" in reply_data)
