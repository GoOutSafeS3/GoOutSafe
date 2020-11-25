import unittest
from monolith.app import create_app
from flask_test_with_csrf import FlaskClient
from flask import url_for
from flask_login import current_user
from utils import do_login, do_logout, get_my_restaurant_id, get_restaurant_rating
from time import sleep

class TestLogin(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.app = create_app()
        self.app.test_client_class = FlaskClient

    # def test_rating_get(self):
    #     client = self.app.test_client()
    #     client.set_app(self.app)
    #     do_login(client,"operator@example.com", "operator")
    #     rest_id = get_my_restaurant_id(client)
        
    #     check_ratings.apply()
        
    #     self.assertIsNotNone(rest_id)
    #     rate = get_restaurant_rating(client, rest_id)
    #     self.assertIsNotNone(rate)
    #     self.assertEqual(4, rate)
        
    # def test_rating_update(self):
    #     client = self.app.test_client()
    #     client.set_app(self.app)
    #     do_login(client,"operator@example.com", "operator")
    #     rest_id = get_my_restaurant_id(client)
    #     self.assertIsNotNone(rest_id)
    #     rate = get_restaurant_rating(client, rest_id)
    #     self.assertIsNotNone(rate)
    #     self.assertEqual(5, rate)

    #     reply = client.t_post("/restaurants/%d/rate"%rest_id, data = {"rating": "1"})
    #     self.assertEqual(reply.status_code, 200)

    #     check_ratings.apply()

    #     rate = get_restaurant_rating(client, rest_id)
    #     self.assertIsNotNone(rate)
    #     self.assertEqual(3, rate)


    # def test_rating_recompute(self):
    #     client = self.app.test_client()
    #     client.set_app(self.app)
    #     do_login(client,"operator@example.com", "operator")
    #     rest_id = get_my_restaurant_id(client)
        
    #     recompute_ratings.apply()
        
    #     self.assertIsNotNone(rest_id)
    #     rate = get_restaurant_rating(client, rest_id)
    #     self.assertIsNotNone(rate)
    #     self.assertEqual(5, rate)

    def test_rating_get(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client,"operator@example.com", "operator")
        rest_id = get_my_restaurant_id(client)
        
        self.assertIsNotNone(rest_id)
        rate = get_restaurant_rating(client, rest_id)
        self.assertIsNotNone(rate)
        self.assertEqual(0, rate)

        do_logout(client)

        do_login(client,"operator2@example.com", "operator")
        rest_id = get_my_restaurant_id(client)
        
        self.assertIsNotNone(rest_id)
        # assuming  test_can_rate_once is done before
        # wait the necessary time max 10 seconds
        for i in range(10):
            sleep(1)
            rate = get_restaurant_rating(client, rest_id)
            self.assertIsNotNone(rate)
            if int(rate) == 4:
                break
        self.assertEqual(4, int(rate)) 

    def test_rating_postmy(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client,"operator@example.com", "operator")
        rest_id = get_my_restaurant_id(client)
        self.assertIsNotNone(rest_id)

        reply = client.t_post(f"/restaurants/{rest_id}/rate", data = {"rating": "5"})
        self.assertEqual(reply.status_code, 200)

    def test_can_rate_once(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            reply = do_login(client, "admin@example.com", "admin")
            
            reply = client.t_post("/restaurants/2/rate", data = {"rating": "5"})
            self.assertEqual(reply.status_code, 200)
            
            reply = client.t_post("/restaurants/2/rate", data = {"rating": "5"})
            self.assertEqual(reply.status_code, 400)

    def test_rating_wrong(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            reply = do_login(client, "admin@example.com", "admin")
            
            reply = client.t_post("/restaurants/2/rate", data = {"rating": None})
            self.assertEqual(reply.status_code, 400)