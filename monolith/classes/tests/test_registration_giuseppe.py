import unittest
import json
from flask import request, jsonify
from monolith.app import create_app_testing
from bs4 import BeautifulSoup
import inspect

app = create_app_testing()
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False #GB Why?

def log(name, text):
    with open("test.txt", "a") as f:
            f.write("-------------------------------------\n")
            f.write(str(name)+"\n")
            f.write("-------------------------------------\n")
            f.write(str(text)+"\n\n")

class TestRegistration(unittest.TestCase):

    def send_registration_form(self, email, firstname, lastname, password, password_repeat, telephone, dateofbirth):
        tested_app = app.test_client()
        form = {
            "email":email,
            "firstname":firstname,
            "lastname":lastname,
            "password":password,
            "dateofbirth":dateofbirth,
            "telephone":telephone,
            "password_repeat":password_repeat,
        }
        reply = tested_app.post('/create_user', data=form)

        soup = BeautifulSoup(reply.get_data(as_text=True), 'html.parser')
        helpblock = soup.find_all('p', attrs={'class': 'help-block'})

        if helpblock == []:
            helpblock = ""
        else:
            helpblock = helpblock[0].text.strip()

        return {"status_code":reply.status_code, "help-block":helpblock}

    def test_good_form(self):
        reply = self.send_registration_form("testerGoodForm@test.me","Tester", "GF", "42","42","123456","01/01/1970")
        log(inspect.stack()[0][3],reply)
        
        self.assertEqual(
            reply["status_code"],
            200)
        self.assertEqual(
            reply["help-block"],
            '')

    def test_existing_email(self):
        reply = self.send_registration_form("example@example.com","Tester", "EE", "42","42","123456","01/01/1970")
        log(inspect.stack()[0][3],reply)
        self.assertEqual(
            reply["status_code"],
            400)
        self.assertEqual(
            reply["help-block"],
            'error, Existing user')

    def test_existing_name_surname_user(self):
        reply = self.send_registration_form("testerExistingNameSurname@tester.com","Tester", "GF", "42","42","123456","01/01/1970")
        log(inspect.stack()[0][3],reply)
        self.assertEqual(
            reply["status_code"],
            200) 
        self.assertEqual(
            reply["help-block"],
            '') 

    def test_wrong_dateofbirth(self):
        reply = self.send_registration_form("testerWrongDateOfBirth@test.me","Tester", "DoB", "42","42","123456","thisisadateofbirth")
        log(inspect.stack()[0][3],reply)
        self.assertEqual(
            reply["status_code"],
            200) #GB to change in 400?
        self.assertEqual(
            reply["help-block"],
            'Not a valid date value')

    def test_wrong_repeated_password(self):
        reply = self.send_registration_form("testerWrongRepeatedPassword@test.me","Tester", "WRP", "42","43","123456","01/01/1970")
        log(inspect.stack()[0][3],reply)
        self.assertEqual(
            reply["status_code"],
            200) #GB to change in 400?
        self.assertEqual(
            reply["help-block"],
            'warning, Passwords do not match')

    def test_wrong_email(self):
        reply = self.send_registration_form("testerWorngEmail.test.me","tester", "WE", "42","42","123456","123456""01/01/1970")
        log(inspect.stack()[0][3],reply)
        self.assertEqual(
            reply["status_code"],
            200) #GB 200 like dateofbirth or 400?
        self.assertEqual(
            reply["help-block"],
            'Invalid email address.') #GB Need a control like this


if __name__ == '__main__':
    unittest.main()