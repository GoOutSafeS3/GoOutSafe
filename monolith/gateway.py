from datetime import datetime
from monolith.utilities.gateway_interface import GatewayInterface
from monolith.utilities.request_timeout import get, post, put, patch, delete
from flask import g

def get_getaway():
    if 'gateway' not in g:
        g.gateway = RealGateway("https://gateway.local:8080")

    return g.gateway

class RealGateway(GatewayInterface):
    def __init__(self, gateway_addr):
        self.addr = gateway_addr
    
    #### USERS ####
    def get_user(self, user_id: int):
        return get(f"{self.addr}/users/{user_id}")

    # TODO
    def search_users(self, data):
        pass

    def get_users(self):
        return get(f"{self.addr}/users")

    def _create_user(self, userdata):
        return post(f"{self.addr}/users", userdata)
    
    # TODO
    def login_user(self, userdata):
        pass

    #### CONTACT TRACING ####
    def get_positive_users(self):
        return get(f"{self.addr}/users?is_positive=true")

    def get_user_contacts(self, user_id, begin, end):
        return get(f"{self.addr}/users/{user_id}/contacts?begin={begin}&end={end}")

    # TODO
    def mark_user(self, user_id):
        pass

    # TODO
    def unmark_user(self, user_id):
        pass

    #### NOTIFICATIONS ####
    def get_notifications(self, user_id: int, read: int = None):
        base_url = f"{self.addr}/notifications?user_id={user_id}"
        if read is not None:
            base_url += f"&read={'true' if read else 'false'}"
        return get(base_url)

    def get_notification(self, notification_id: int):
        return get(f"{self.addr}/notifications/{notification_id}")

    def mark_notif_as_read(self, notification_id: int):
        now = datetime.now().isoformat()
        return patch(f"{self.addr}/notifications/{notification_id}",
            {
                "read_on": now
            })

    #### RESTAURANTS ####
    def get_restaurants(self):
        return get(f"{self.addr}/restaurants")

    def get_restaurant(self, rest_id):
        return get(f"{self.addr}/restaurants/{rest_id}")

    def get_user_future_reservations(self, user_id):
        today = datetime.today().isoformat()
        return get(f"{self.addr}/bookings?user={user_id}&from={today}")

    #### RESERVATIONS ####
    def get_bookings(self, user=None, rest=None, table=None, begin=None, end=None, begin_entrance=None, end_entrance=None, with_user=True):
        url = self.addr+"bookings?"

        if user is not None:
            url += "user="+str(user)+"&"

        if rest is not None:
            url += "rest="+str(rest)+"&"

        if table is not None:
            url += "table="+str(table)+"&"

        if begin is not None:
            url += "begin="+str(begin)+"&"

        if end is not None:
            url += "end="+str(end)+"&"

        if begin_entrance is not None:
            url += "begin_entrance="+str(begin_entrance)+"&"

        if end_entrance is not None:
            url += "end_entrance="+str(end_entrance)+"&"
            
        if with_user:
            url += "with_user=true"

        return get(url)

    def get_a_booking(self, id, with_user=True):
        url = self.addr+"bookings/"+str(id)
        if with_user:
            url += "?with_user=true"
        return get(url)

    def new_booking(self, user_id, rest_id, number_of_people, booking_datetime):
        booking = {
            "user_id":user_id,
            "restaurant_id":rest_id,
            "number_of_people":number_of_people,
            "booking_datetime":booking_datetime,
        }

        return post(self.addr+"bookings",booking)

    def edit_booking(self, booking_id, number_of_people=None, booking_datetime=None, entrance=False):
        booking = {
        }

        if number_of_people is not None:
            booking["number_of_people"] = number_of_people

        if booking_datetime is not None:
            booking["booking_datetime"] = booking_datetime

        url = self.addr+"bookings/"+str(booking_id)

        if entrance:
            url += "?entrance=true"

        return put(url,booking)

    def delete_booking(self, id):
        return delete(self.addr+"bookings/"+str(id))