import unittest
from monolith.app import create_app_testing
from flask_test_with_csrf import FlaskClient
from flask import url_for
from flask_login import current_user
import re

class TestLogin(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.app = create_app_testing()
        self.app.test_client_class = FlaskClient
    
    def test_endpoints(self):
        def get_url_mappings(app ,rule_filter=None):
            rule_filter = rule_filter or (lambda rule: True)
            app_rules = [
                rule for rule in app.url_map.iter_rules()
                if rule_filter(rule)
            ]
            return app_rules
        for rule in get_url_mappings(self.app):
            url = re.sub('<[a-z:_]*>',"99999",str(rule))
            if url != str(rule):
                client = self.app.test_client()
                client.set_app(self.app)
                client.t_post('/login',data={"email":"operator@example.com", "password": "operator"})
                reply = client.t_get(url)
                self.assertEqual(reply.status_code, 404, msg=url+reply.get_data(as_text=True))