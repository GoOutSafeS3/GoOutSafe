import unittest
import json
from flask import request, jsonify
from monolith.app import create_app_testing
from flask_test_with_csrf import FlaskClient
from bs4 import BeautifulSoup
import inspect

class TestRegistration(unittest.TestCase):
    def send_registration_form(self, tested_app, url, form):

        reply = tested_app.t_post(url, data=form)
        soup = BeautifulSoup(reply.get_data(as_text=True), 'html.parser')
        helpblock = soup.find_all('p', attrs={'class': 'help-block'})

        if helpblock == []:
            helpblock = ""
        else:
            helpblock = helpblock[0].text.strip()

        return {"status_code":reply.status_code, "help-block":helpblock}

    def setup_app(self):
        app = create_app_testing()
        app.test_client_class = FlaskClient
        tested_app = app.test_client()
        tested_app.set_app(app)

        form = {
            "email":"testerGoodFormOperator@test.me",
            "firstname":"Tester",
            "lastname":"OGF",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
            "restaurant_name":"Restaurant at the End of the Universe",
            "restaurant_phone":"1234567890",
            "restaurant_latitude":"43.431489",
            "restaurant_longitude":"10.242911",
        }

        reply = self.send_registration_form(tested_app, '/create_operator', form)
        
        self.assertEqual(
            reply["status_code"],
            200,msg=reply)
        self.assertEqual(
            reply["help-block"],
            'success, Operator registerd succesfully')
        return tested_app

    def do_login(self,client, email, password):
        return client.t_post('/login',data={"email":email, "password": password})

    def get_my_restaurant_id(self, client):
        #alrady logged as we created a user right now
        reply = client.get('/')
        text = reply.get_data(as_text=True)
        id = text[text.find("/restaurants/")+len("/restaurants/"):].split("\"")[0]
        try:
            id = int(id)
        except:
            self.fail(msg="id not integer "+str(id)+" "+text)
        return id

    def test_get_edit_id(self):
        client = self.setup_app()
        self.do_login(client,"testerGoodFormOperator@test.me", "42")
        id = self.get_my_restaurant_id(client)
