import unittest
from monolith.app import create_app_testing
from flask_test_with_csrf import FlaskClient


class TestReservation(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.app = create_app_testing()
        self.app.test_client_class = FlaskClient

    def test_can_booking(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "customer@example.com",
                "password":"customer"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)
            form = {
                "number_of_person": "2",
                "booking_date": "04/10/2022",
                "booking_hr": "13",
                "booking_min": "30"
            }
            reply = client.t_post("/restaurants/1/book", data=form)
            self.assertEqual(reply.status_code, 302)

    def test_booking_restaurantNone(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "customer@example.com",
                "password":"customer"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)
            form = {
                "number_of_person": "2",
                "booking_date": "04/10/2022",
                "booking_hr": "13",
                "booking_min": "30"
            }
            reply = client.t_post("/restaurants/55654/book", data=form)
            self.assertEqual(reply.status_code, 404)

    def test_cannot_booking_admin(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "example@example.com",
                "password":"admin"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)
            reply = client.t_get("/restaurants/1/book", data=form)
            self.assertEqual(reply.status_code, 401)

    def test_cannot_booking_positive(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "positive@example.com",
                "password": "positive"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)
            reply = client.t_get("/restaurants/1/book")
            self.assertEqual(reply.status_code, 401)

    def test_get_booking_page(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "customer@example.com",
                "password":"customer"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)
            reply = client.t_get("/restaurants/1/book", data=form)
            self.assertEqual(reply.status_code, 200)

    def test_cannot_booking(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "customer@example.com",
                "password":"customer"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)
            form = {
                "number_of_person": "500",
                "booking_date": "04/10/2022",
                "booking_hr": "13",
                "booking_min": "30"
            }
            reply = client.t_post("/restaurants/1/book", data=form)
            self.assertEqual(reply.status_code, 400)

    def test_cannot_booking_date(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "customer@example.com",
                "password":"customer"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)
            form = {
                "number_of_person": "2",
                "booking_date": "04/10/2010",
                "booking_hr": "13",
                "booking_min": "30"
            }
            reply = client.t_post("/restaurants/1/book", data=form)
            self.assertEqual(reply.status_code, 400)

    def test_reservation_not_operator(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "example@example.com",
                "password":"admin"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)
            reply = client.t_get("/restaurants/1/reservations", data=form)
            self.assertEqual(reply.status_code, 401)

    def test_reservation_none_restaurants(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "operator@example.com",
                "password":"operator"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)
            reply = client.t_get("/restaurants/37923/reservations", data=form)
            self.assertEqual(reply.status_code, 404)

    def test_reservation_another_operator(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "operator2@example.com",
                "password":"operator2"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)
            reply = client.t_get("/restaurants/1/reservations", data=form)
            self.assertEqual(reply.status_code, 401)

    def test_get_reservation_list_operator(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "operator@example.com",
                "password":"operator"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)
            reply = client.t_get("/restaurants/1/reservations", data=form)
            self.assertEqual(reply.status_code, 200)

    def test_bad_reservation_list(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "operator@example.com",
                "password":"operator"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)

            form = {
                "from_date":"10/10/2020",
                "from_hr":"13",
                "from_min":"30",
                "to_date":"08/10/2020",
                "to_hr":"14",
                "to_min":"30"
            }
            reply = client.t_post("/restaurants/1/reservations", data=form)
            self.assertEqual(reply.status_code, 400)

    def test_good_reservation_list(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "operator@example.com",
                "password": "operator"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)

            form = {
                "from_date": "08/10/2020",
                "from_hr": "13",
                "from_min": "30",
                "to_date": "10/10/2020",
                "to_hr": "14",
                "to_min": "30"
            }
            reply = client.t_post("/restaurants/1/reservations", data=form)
            self.assertEqual(reply.status_code, 200)

    def test_bad_reservations_id(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "operator@example.com",
                "password": "operator"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)

            reply = client.t_get("/restaurants/479432")
            self.assertEqual(reply.status_code, 404)

    def test_good_reservations_id(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "operator@example.com",
                "password": "operator"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)

            reply = client.t_get("/restaurants/1")
            self.assertEqual(reply.status_code, 200)

    def test_rese_id_none(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "operator@example.com",
                "password": "operator"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)

            reply = client.t_get("/reservations/168012")
            self.assertEqual(reply.status_code, 404)

    def test_bad_rese_id(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "operator2@example.com",
                "password": "operator2"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)

            reply = client.t_get("/reservations/1")
            self.assertEqual(reply.status_code, 401)

    def test_rese_delete(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "operator@example.com",
                "password": "operator"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)

            reply = client.t_post("/reservations/1")
            self.assertEqual(reply.status_code, 302)

if __name__ == '__main__':
    unittest.main()
