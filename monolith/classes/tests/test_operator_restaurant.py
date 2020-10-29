import unittest
import json
from flask import request, jsonify
from monolith.app import create_app_testing
from flask_test_with_csrf import FlaskClient
from bs4 import BeautifulSoup
import inspect

class TestRegistration(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.app = create_app_testing()
        self.app.test_client_class = FlaskClient

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
        self.app = create_app_testing()
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

        form = {
            "email":"testerGoodFormOperator2@test.me",
            "firstname":"Tester2",
            "lastname":"OGF2",
            "password":"42",
            "password_repeat":"42",
            "dateofbirth":"01/01/1970",
            "telephone":"1234567890",
            "restaurant_name":"Restaurant at the End of the Pizza",
            "restaurant_phone":"1234567891",
            "restaurant_latitude":"43.431481",
            "restaurant_longitude":"10.242915",
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
        reply = client.t_get('/')
        text = reply.get_data(as_text=True)

        id = text[text.find("/restaurants/")+len("/restaurants/"):].split("\"")[0]
        try:
            id = int(id)
        except:
            self.fail(msg="id not integer "+str(id)+" "+text)
        return id

    def edit_restaurant(self, client, id, data):
        return client.t_post("/restaurants/"+str(id)+"/edit", data=data)


    def test_get_edit_id(self):
        client = self.setup_app()
        self.do_login(client,"testerGoodFormOperator@test.me", "42")
        id = self.get_my_restaurant_id(client)
        reply = client.t_get('/restaurants/'+str(id)+"/edit")
        self.assertEqual(reply.status_code, 200, msg=reply.get_data(as_text=True))

    def test_post_edit(self):
        client = self.setup_app()
        self.do_login(client,"testerGoodFormOperator@test.me", "42")
        id = self.get_my_restaurant_id(client)
        form = {
            "name":"Restaurant at the End of the Universe",
            "phone":"1234567890",
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
        reply = self.edit_restaurant(client, id, form.copy())
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

    def test_post_edit_wrong_user(self):
        client = self.setup_app()
        self.do_login(client,"testerGoodFormOperator2@test.me", "42")
        id = self.get_my_restaurant_id(client)
        form = {
            "name":"Restaurant at the End of the Universe",
            "phone":"1234567890",
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
        reply = self.edit_restaurant(client, id-1, form.copy()) #id-1 because id is the restorant of operato2
        self.assertEqual(reply.status_code, 401, msg=reply.get_data(as_text=True))


    def test_post_edit_wrong_data(self):
        client = self.setup_app()
        self.do_login(client,"testerGoodFormOperator@test.me", "42")
        id = self.get_my_restaurant_id(client)
        form = {
            "name": None,
            "phone":"1234567890",
            "lat":"43.431489",
            "lon":"10.242911",
            "opening_hour_lunch": "13",
            "closing_hour_lunch": "15",
            "opening_hour_dinner": "19",
            "closing_hour_dinner": "23",
            "occupation_time": "2",
            "closed_days": ["1","2"],
            "cuisine_type": "None",
            "menu": "None"
        }
        for k,v in form.items():
            dup = form.copy()
            dup[k] = None
            reply = self.edit_restaurant(client, id, dup)
            self.assertEqual(reply.status_code, 400, msg=reply.get_data(as_text=True))