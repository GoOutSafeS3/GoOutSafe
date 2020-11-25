import unittest
from monolith.app import create_app
from flask_test_with_csrf import FlaskClient
from flask import url_for
from flask_login import current_user
from utils import do_login, do_logout, get_positives_id

import datetime
class TestLogin(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.app = create_app()
        self.app.test_client_class = FlaskClient

    def test_unhautorized_access(self):
        client = self.app.test_client()
        client.set_app(self.app)

        users = ["admin@example.com","gianni@example.com","operator@example.com"]
        passw = ["admin","gianni","operator"]
        endpoints = ["/positives","/positives/mark","/positives/unmark","/positives/1/unmark", "/positives/contacts"]

        for i in range(len(users)):
            do_login(client, users[i], passw[i])
            for e in endpoints:
                reply = client.t_get(e)
                self.assertEqual(reply.status_code, 401, msg="endpoint: "+e+"\n"+reply.get_data(as_text=True))
            do_logout(client)


    def test_HA_access(self):
        client = self.app.test_client()
        client.set_app(self.app)

        endpoints = ["/positives","/positives/mark","/positives/unmark", "/positives/contacts"]

        do_login(client, "health@example.com", "health")
        for e in endpoints:
            reply = client.t_get(e)
            self.assertEqual(reply.status_code, 200, msg="endpoint: "+e+"\n"+reply.get_data(as_text=True))
        do_logout(client)

    def test_positives_list(self):
        client = self.app.test_client()
        client.set_app(self.app)

        do_login(client, "health@example.com", "health")
        reply = client.t_get("/positives")
        self.assertIn("Alice Vecchio",reply.get_data(as_text=True), msg=reply.get_data(as_text=True))
        do_logout(client)

    def test_mark_unmark_mail(self):
        client = self.app.test_client()
        client.set_app(self.app)

        endpoints = ["/positives/mark","/positives/unmark"]

        do_login(client, "health@example.com", "health")

        form = {
            "email":"gianni@example.com",
            "telephone":"",
            "ssn":""
            }

        for e in endpoints:
            reply = client.t_post(e,form)
            self.assertEqual(reply.status_code, 302, msg="endpoint: "+e+"\n"+reply.get_data(as_text=True))
            self.assertEqual(reply.location, "http://localhost/positives", msg=reply.location)
        do_logout(client)

    def test_mark_unmark_telephone(self):
        client = self.app.test_client()
        client.set_app(self.app)

        endpoints = ["/positives/mark","/positives/unmark"]

        do_login(client, "health@example.com", "health")

        form = {
            "email":"",
            "telephone":"46966711",
            "ssn":""
            }

        for e in endpoints:
            reply = client.t_post(e,form)
            self.assertEqual(reply.status_code, 302, msg="endpoint: "+e+"\n"+reply.get_data(as_text=True))
            self.assertEqual(reply.location, "http://localhost/positives", msg=reply.location)
        do_logout(client)

    def test_mark_unmark_ssn(self):
        client = self.app.test_client()
        client.set_app(self.app)

        endpoints = ["/positives/mark","/positives/unmark"]

        do_login(client, "health@example.com", "health")

        form = {
            "email":"",
            "telephone":"",
            "ssn":"ANNASSN4791DFGYU"
            }

        for e in endpoints:
            reply = client.t_post(e,form)
            self.assertEqual(reply.status_code, 302, msg="endpoint: "+e+"\n"+reply.get_data(as_text=True))
            self.assertEqual(reply.location, "http://localhost/positives", msg=reply.location)
        do_logout(client)

    def test_mark_unmark_conflicting_data(self):
        client = self.app.test_client()
        client.set_app(self.app)

        endpoints = ["/positives/mark","/positives/unmark", "/positives/contacts"]

        do_login(client, "health@example.com", "health")

        form = {
            "email":"gianni@example.com",
            "telephone":"3939675681",
            "ssn":"ANNASSN4791DFGYU"
            }

        for e in endpoints:
            reply = client.t_post(e,form)
            self.assertEqual(reply.status_code, 200, msg="endpoint: "+e+"\n"+reply.get_data(as_text=True))
            self.assertIn("User not found",reply.get_data(as_text=True), msg=reply.get_data(as_text=True))
        do_logout(client)

    def test_mark_unmark_empty_field(self):
        client = self.app.test_client()
        client.set_app(self.app)

        endpoints = ["/positives/mark","/positives/unmark", "/positives/contacts"]

        do_login(client, "health@example.com", "health")

        form = {
            "email":"",
            "telephone":"",
            "ssn":""
            }

        for e in endpoints:
            reply = client.t_post(e,form)
            self.assertEqual(reply.status_code, 400, msg="endpoint: "+e+"\n"+reply.get_data(as_text=True))
            self.assertIn("Please fill in a field", reply.get_data(as_text=True), msg=reply.get_data(as_text=True))
        do_logout(client)


    def test_mark_unmark_wrong_mail(self):
        client = self.app.test_client()
        client.set_app(self.app)

        endpoints = ["/positives/mark","/positives/unmark", "/positives/contacts"]

        do_login(client, "health@example.com", "health")

        form = {
            "email":"the_customer@example.com",
            "telephone":"",
            "ssn":""
            }

        for e in endpoints:
            reply = client.t_post(e,form)
            self.assertEqual(reply.status_code, 200, msg="endpoint: "+e+"\n"+reply.get_data(as_text=True))
            self.assertIn("User not found",reply.get_data(as_text=True), msg=reply.get_data(as_text=True))
        do_logout(client)

    def test_mark_unmark_bad_form(self):
        client = self.app.test_client()
        client.set_app(self.app)

        endpoints = ["/positives/mark","positives/unmark", "/positives/contacts"]

        do_login(client, "health@example.com", "health")

        form = {
            "email":"",
            "telephone":"",
            "ssn":""
            }

        for f in ["email","telephone","ssn"]:
            bad_form = form
            bad_form[f] = None
            for e in endpoints:
                reply = client.t_post(e,bad_form)
                self.assertEqual(reply.status_code, 400, msg="form: "+str(bad_form)+"\nendpoint: "+e+"\n"+reply.get_data(as_text=True))
                self.assertIn("Bad Form",reply.get_data(as_text=True),  msg="endpoint: "+e+"\n"+reply.get_data(as_text=True))
    

        bad_form = form
        bad_form["dateofbirth"] = "01/01/1969"
        for e in endpoints:
            reply = client.t_post(e,bad_form)
            self.assertEqual(reply.status_code, 400, msg="form: "+str(bad_form)+"\nendpoint: "+e+"\n"+reply.get_data(as_text=True))
            self.assertIn("Bad Form",reply.get_data(as_text=True),  msg="endpoint: "+e+"\n"+reply.get_data(as_text=True))
        
        do_logout(client)

    def test_unmark_not_positive(self):
        client = self.app.test_client()
        client.set_app(self.app)

        endpoints = ["/positives/mark","/positives/unmark", "/positives/contacts"]

        do_login(client, "health@example.com", "health")

        form = {
            "email":"gianni@example.com",
            "telephone":"",
            "ssn":""
            }

        client.t_post("/positives/unmark",form) # now we're sure the user isn't marked
        reply = client.t_post("/positives/unmark",form)
        self.assertEqual(reply.status_code, 200, msg=reply.get_data(as_text=True))
        self.assertIn("The user is not positive", reply.get_data(as_text=True), msg=reply.get_data(as_text=True))
        do_logout(client)


    def test_mark_with_id(self):
        client = self.app.test_client()
        client.set_app(self.app)

        do_login(client, "health@example.com", "health")

        reply = client.t_get(f"/positives/1/mark")
        self.assertEqual(reply.status_code, 302, msg=reply.get_data(as_text=True))
        self.assertEqual(reply.location, "http://localhost/positives", msg=reply.location)
        do_logout(client)


    def test_mark_with_id_404(self):
        client = self.app.test_client()
        client.set_app(self.app)

        do_login(client, "health@example.com", "health")
        reply = client.t_get(f"/positives/99999/mark")
        self.assertEqual(reply.status_code, 404, msg=reply.get_data(as_text=True))
        do_logout(client)

    def test_unmark_with_id(self):
        client = self.app.test_client()
        client.set_app(self.app)

        do_login(client, "health@example.com", "health")

        form = {
            "email":"gianni@example.com",
            "telephone":"",
            "ssn":""
            }

        client.t_post("/positives/mark",form) # now we're sure that there is at least one positive user
        match = get_positives_id(client)[0]
        reply = client.t_get(f"/positives/{match}/unmark")
        self.assertEqual(reply.status_code, 302, msg=reply.get_data(as_text=True))
        self.assertEqual(reply.location, "http://localhost/positives", msg=reply.location)
        do_logout(client)


    def test_unmark_with_id_404(self):
        client = self.app.test_client()
        client.set_app(self.app)

        do_login(client, "health@example.com", "health")
        reply = client.t_get(f"/positives/99999/unmark")
        self.assertEqual(reply.status_code, 404, msg=reply.get_data(as_text=True))
        do_logout(client)


    def test_unmark_with_not_positive_id(self):
        client = self.app.test_client()
        client.set_app(self.app)

        do_login(client, "health@example.com", "health")

        form = {
            "email":"gianni@example.com",
            "telephone":"",
            "ssn":""
            }

        client.t_post("/positives/mark",form) # now we're sure that there is at least one positive user
        match = get_positives_id(client)[0]
        client.t_get(f"/positives/{match}/unmark") # now the user is unmarked 

        reply = client.t_get(f"/positives/{match}/unmark")
        self.assertEqual(reply.status_code, 404, msg=reply.get_data(as_text=True))
        do_logout(client)

    def test_contacts_need_ha(self):
        client = self.app.test_client()
        client.set_app(self.app)

        do_login(client, "gianni@example.com", "gianni")
        reply = client.t_get(f"/positives/7/contacts")
        self.assertEqual(reply.status_code, 401)
        do_logout(client)

        do_login(client, "health@example.com", "health")
        reply = client.t_get(f"/positives/13/contacts")
        self.assertEqual(reply.status_code, 200)
        do_logout(client)


    def test_contacts_by_mail(self):
        client = self.app.test_client()
        client.set_app(self.app)

        do_login(client, "health@example.com", "health")

        form = {
            "email":"alice@example.com",
            "telephone":"",
            "ssn":""
            }
        reply = client.t_post("/positives/contacts",form)
        self.assertEqual(reply.status_code,302,msg=reply.get_data(as_text=True))    
        do_logout(client)

    def test_contacts_by_telephone(self):
        client = self.app.test_client()
        client.set_app(self.app)

        do_login(client, "health@example.com", "health")

        form = {
            "email":"",
            "telephone":"463366711",
            "ssn":""
            }
        reply = client.t_post("/positives/contacts",form)
        self.assertEqual(reply.status_code,302,msg=reply.get_data(as_text=True))    
        do_logout(client)

    def test_contacts_by_ssn(self):
        client = self.app.test_client()
        client.set_app(self.app)

        do_login(client, "health@example.com", "health")

        form = {
            "email":"",
            "telephone":"",
            "ssn":"TESTALICESSN"
            }
        reply = client.t_post("/positives/contacts",form)
        self.assertEqual(reply.status_code,302,msg=reply.get_data(as_text=True))    
        do_logout(client)

    def test_contacts_not_positive_user(self):
        client = self.app.test_client()
        client.set_app(self.app)

        do_login(client, "health@example.com", "health")

        form = {
            "email":"gianni@example.com",
            "telephone":"",
            "ssn":""
            }
        reply = client.t_post("/positives/contacts",form)
        self.assertEqual(reply.status_code,200,msg=reply.get_data(as_text=True))   
        self.assertIn("The user is not positive",reply.get_data(as_text=True),msg=reply.get_data(as_text=True)) 
        do_logout(client)

    def test_contacts_not_positive_user_by_id(self):
        client = self.app.test_client()
        client.set_app(self.app)

        do_login(client, "health@example.com", "health")

        reply = client.t_get("/positives/3/contacts")
        self.assertEqual(reply.status_code,404,msg=reply.get_data(as_text=True))   
        do_logout(client)


    def test_contacts_by_id_404(self):
        client = self.app.test_client()
        client.set_app(self.app)

        do_login(client, "health@example.com", "health")

        reply = client.t_get("/positives/99999/contacts")
        self.assertEqual(reply.status_code,404,msg=reply.get_data(as_text=True))   
        do_logout(client)