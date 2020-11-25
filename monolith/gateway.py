from datetime import datetime
from monolith.utilities.gateway_interface import GatewayInterface
from monolith.utilities.request_timeout import get, post, put, patch, delete
from flask import g


def get_getaway() -> GatewayInterface:
    if 'gateway' not in g:
        g.gateway = RealGateway("http://api:5000")

    return g.gateway


class RealGateway(GatewayInterface):
    def __init__(self, gateway_addr):
        self.addr = gateway_addr

    #### USERS ####
    def get_user(self, user_id: int):
        return get(f"{self.addr}/users/{user_id}")

    def get_users(self, ssn=None, phone=None, email=None, is_positive=None):
        url = self.addr + "/users"
        params = '?'
        if ssn is not None:
            params += 'ssn=' + str(ssn) + '&'

        if phone is not None:
            params += 'phone=' + str(phone) + '&'

        if email is not None:
            params += 'email=' + str(email) + '&'

        if is_positive is True:
            params += 'is_positive=True'
        elif is_positive is False:
            params += 'is_positive=False'

        return get(url + params)

    def create_user(self, userdata):
        return post(url= self.addr + '/users', json=userdata)

    def edit_user(self, user_id, userdata):
        return put(f"{self.addr}/users/"+str(user_id), json=userdata)

    def delete_user(self, user_id):
        return delete(self.addr + '/users/' + str(user_id))

    def set_user_restaurant(self, user_id, rest_id):
        user,status = self.get_user(user_id)
        if user is None or status != 200:
            return None, 500
        if user['is_operator']:
            user = user.toDict()
            els = ["email", "firstname", "lastname", "phone", "dateofbirth", "password"]
            arr = []
            for k,v in user.items():
                if k not in els:
                    arr.append(k)
            for a in arr:
                del user[a]
            user['rest_id'] = rest_id
            return put(f"{self.addr}/users/{user_id}", json=user)
        else:
            return None, 400


    #### CONTACT TRACING ####

    def get_positive_users(self):
        return get(f"{self.addr}/users?is_positive=True")

    def get_user_contacts(self, user_id, begin, end):
        return get(f"{self.addr}/users/{user_id}/contacts?begin={begin}&end={end}")

    def mark_user(self, user_id):
        user, status = get(f"{self.addr}/users/" + str(user_id))
        if status != 200 or user is None:
            return None, None
        user['is_positive'] = True
        user['positive_datetime'] = datetime.today().isoformat()
        return put(f"{self.addr}/users/" + str(user_id), json=user)

    def unmark_user(self, user_id):
        user, status = get(f"{self.addr}/users/" + str(user_id))
        user['is_positive'] = False
        return put(f"{self.addr}/users/" + str(user_id), json=user)

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
    def get_restaurants(self, name=None, opening_time=None, open_day=None, cuisine_type=None, menu=None):
        url = f"{self.addr}/restaurants?"
        if name is not None:
            url += "name=" + str(name) + "&"
        if opening_time is not None:
            url += "opening_time=" + str(opening_time) + "&"
        if open_day is not None:
            url += "open_day=" + str(open_day) + "&"
        if cuisine_type is not None:
            url += "cuisine_type=" + str(cuisine_type) + "&"
        if menu is not None:
            url += "menu=" + str(menu) + "&"
        if url[-1] == "&":
            url = url[:-1]
        if url[-1] == "?":
            url = url[:-1]
        return get(url)

    def post_restaurants(self, json):
        return post(f"{self.addr}/restaurants", json=json)

    def get_restaurant(self, rest_id):
        return get(f"{self.addr}/restaurants/{rest_id}")

    def edit_restaurant(self, rest_id, json):
        return put(f"{self.addr}/restaurants/{rest_id}", json=json)

    def delete_restaurant(self,rest_id):
        url = f"{self.addr}/restaurants/{rest_id}"
        return delete(url)

    def get_restaurant_rate(self, rest_id):
        return get(f"{self.addr}/restaurants/{rest_id}/rate")

    def post_restaurant_rate(self, rest_id, rater_id,rating):
        return post(f"{self.addr}/restaurants/{rest_id}/rate", json={"rater_id":rater_id, "rating":rating })        

    #### TABLES ####
    def get_restaurants_tables(self, rest_id, capacity=None):
        url = f"{self.addr}/restaurants/{rest_id}/tables?"
        if capacity is not None:
            url += "capacity=" + str(capacity)
        if url[-1] == "?":
            url = url[:-1]
        return get(url)

    def post_restaurants_tables(self, rest_id, capacity):
        url = f"{self.addr}/restaurants/{rest_id}/tables"
        return post(url, json={"capacity": capacity})

    def get_restaurants_table(self, rest_id, table_id):
        url = f"{self.addr}/restaurants/{rest_id}/tables{table_id}"
        return get(url)

    def edit_restaurants_table(self, rest_id, table_id, capacity):
        url = f"{self.addr}/restaurants/{rest_id}/tables{table_id}"
        return put(url, json={"capacity": capacity})

    def delete_restaurants_table(self, rest_id, table_id):
        url = f"{self.addr}/restaurants/{rest_id}/tables{table_id}"

    def get_restaurants_table(self,rest_id, table_id):
        url = f"{self.addr}/restaurants/{rest_id}/tables/{table_id}"
        return get(url)
    
    def edit_restaurants_table(self,rest_id, table_id, capacity):
        url = f"{self.addr}/restaurants/{rest_id}/tables/{table_id}"
        return put(url, json={"capacity":capacity})

    def delete_restaurants_table(self,rest_id, table_id):
        url = f"{self.addr}/restaurants/{rest_id}/tables/{table_id}"
        return delete(url)

    #### RESERVATIONS ####
    def get_bookings(self, user=None, rest=None, table=None, begin=None, end=None, begin_entrance=None,
                     end_entrance=None, with_user=True):

        """ Return the list of bookings.

        GET /bookings?[user=U_ID&][rest=R_ID&][table=T_ID&][begin=BEGING_DT&][end=END_DT&][begin_entrance=BEGING_ENT_DT&][end_entrance=END_ENT_DT&][with_user=true/false]

        It's possible to filter the bookings thanks the query's parameters.
        The parameters can be overlapped in any way.
        All paramters are optional.

        - user: All the booking of a specific user (by id)
        - rest: All the booking of a specific restaurant (by id)
        - table: All the booking of a specific table (by id)
        - begin: All bookings from a certain date onwards (datetime ISO 8601 - Chapter 5.6)
        - end: All bookings up to a certain date onwards (datetime ISO 8601 - Chapter 5.6)
        - begin_entrance: All bookings from a certain entrance date onwards (datetime ISO 8601 - Chapter 5.6)
        - end_entrance: All bookings up to a certain entrance date onwards (datetime ISO 8601 - Chapter 5.6)
        - with_user: If true adds at each bookings the user information

        If begin and not end is specified, all those starting from begin are taken. Same thing for end.

        Status Codes:
            200 - OK
            400 - Wrong datetime format
        """

        url = self.addr + "/bookings?"

        if user is not None:
            url += "user=" + str(user) + "&"

        if rest is not None:
            url += "rest=" + str(rest) + "&"

        if table is not None:
            url += "table=" + str(table) + "&"

        if begin is not None:
            url += "begin=" + str(begin) + "&"

        if end is not None:
            url += "end=" + str(end) + "&"

        if begin_entrance is not None:
            url += "begin_entrance=" + str(begin_entrance) + "&"

        if end_entrance is not None:
            url += "end_entrance=" + str(end_entrance) + "&"

        if with_user:
            url += "with_user=true"

        return get(url)

    def get_a_booking(self, id, with_user=True):

        """ Return a specific booking (request by id)

        GET /bookings/{booking_id}?[with_user=true/false]

        - with_user: [optional] If true adds the user information

        Status Codes:
            200 - OK
            404 - Booking not found
        """

        url = self.addr + "/bookings/" + str(id)
        if with_user:
            url += "?with_user=true"
        return get(url)

    def new_booking(self, user_id, rest_id, number_of_people, booking_datetime):

        """ Add a new booking.

        POST /bookings
        
        Returns the booking if it can be made, otherwise returns an error message.

        Requires a json object with:
            - number_of_people: the number of people for the booking
            - booking_datetime: the datetime of the booking
            - user_id: the id of the user who made the booking
            - restaurant_id: the id of the restaurant

        Status Codes:
            201 - The booking has been created
            400 - Wrong datetime
            409 - Impossible to change the booking (it is full, it is closed ...)
            500 - Error in communicating with the restaurant service or problem with the database (try again)
        """

        booking = {
            "user_id": user_id,
            "restaurant_id": rest_id,
            "number_of_people": number_of_people,
            "booking_datetime": booking_datetime,
        }

        return post(self.addr + "/bookings", booking)

    def edit_booking(self, booking_id, number_of_people=None, booking_datetime=None, entrance=False):

        """ Edit a booking.

        GET /bookings/{booking_id}?[entrance=true/false]

        Changes the number of people and/or the date of the booking. 
        Or marks the user's entry.

        The request to mark the entrance is made through the query parameter entrance (a boolean)

        Change requests are made through json objects with the following properties (both optional)
            - booking_datetime: the new requested datetime
            - number_of_people: the new requested number of people

        If one of the two fields is not set, the one already entered is recovered.
        If both are not entered the request is void (unless required to mark the entry()in this case the json is ignored).

        If entry is marked, other requests for changes are ignored (if the user has already entered the changes no longer make sense).
        Likewise, if the entry is marked, no more changes can be made.

        The booking must not have already passed, in the event of a change.

        Change of a booking may not always be possible (on the requested date there are no seats available, the restaurant is closed on that date ...)

        Status Codes:
            200 - OK
            400 - Wrong datetime or bad request (entry already marked)
            404 - Booking not found
            409 - Impossible to change the booking
            500 - Error in communicating with the restaurant service or problem with the database (try again)
        """

        booking = {
        }

        if number_of_people is not None:
            booking["number_of_people"] = number_of_people

        if booking_datetime is not None:
            booking["booking_datetime"] = booking_datetime

        url = self.addr + "/bookings/" + str(booking_id)

        if entrance:
            url += "?entrance=true"

        return put(url, booking)

    def delete_booking(self, id):
        """ Delete a booking specified by the id.

        DELETE /bookings/{booking_id}
        
        Deletion is only possible if the booking has not yet passed.

        Otherwise it remains stored (necessary for contact tracing)

        Status Codes:
            204 - Deleted
            404 - Booking not found
            403 - The booking cannot be deleted: it is a past reservation
            500 - Error with the database
        """
        return delete(self.addr + "/bookings/" + str(id))
