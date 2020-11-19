from datetime import datetime
from monolith.utilities.request_timeout import get, post, put, delete
import datetime

BOOKINGS_SERVICE = "http://172.19.0.1:8080/"

def get_bookings(user=None, rest=None, table=None, begin=None, end=None):
    url = BOOKINGS_SERVICE+"bookings?"

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

    return get(url)

def get_a_booking(id):
    return get(BOOKINGS_SERVICE+"bookings/"+str(id))

def new_booking(user_id, rest_id, number_of_people, booking_datetime):
    booking = {
        "user_id":user_id,
        "restaurant_id":rest_id,
        "number_of_people":number_of_people,
        "booking_datetime":booking_datetime,
    }

    return post(BOOKINGS_SERVICE+"bookings",booking)

def edit_booking(booking_id, number_of_people=None, booking_datetime=None):
    booking = {
    }

    if number_of_people is not None:
        booking["number_of_people"] = number_of_people

    if booking_datetime is not None:
        booking["booking_datetime"] = booking_datetime

    return put(BOOKINGS_SERVICE+"bookings/"+str(booking_id),booking)

def delete_booking(id):
    return delete(BOOKINGS_SERVICE+"bookings/"+str(id))

if __name__ == "__main__":
    print(new_booking(1,3,1,(datetime.datetime.now()+datetime.timedelta(days=2)).isoformat()),"\n")
    print(new_booking(1,3,1,(datetime.datetime.now()+datetime.timedelta(days=2)).isoformat()),"\n")
    print(new_booking(1,3,1,(datetime.datetime.now()+datetime.timedelta(days=2)).isoformat()),"\n")
    print(edit_booking(7,2),"\n")
    print(edit_booking(7,10),"\n")
    print(edit_booking(7,1),"\n")
    print(edit_booking(7,2,(datetime.datetime.now()+datetime.timedelta(days=2,minutes=30)).isoformat()),"\n")
    print(get_bookings(rest=3),"\n")
    print(get_a_booking(1),"\n")
    print(get_a_booking(100),"\n")
    print(new_booking(1,3,1,(datetime.datetime.now()+datetime.timedelta(days=2)).isoformat()),"\n")
    print(edit_booking(1,1),"\n")
    print(edit_booking(7,1),"\n")
    print(edit_booking(7,1),"\n")
    print(edit_booking(1),"\n")
    print(delete_booking(5),"\n")
    print(delete_booking(6),"\n")
    print(get_bookings(),"\n")