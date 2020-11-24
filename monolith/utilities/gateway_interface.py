from abc import ABC, abstractmethod
from werkzeug.security import check_password_hash, generate_password_hash
from typing import Tuple, Dict, List
from datetime import datetime

class GatewayInterface(ABC):
    #### USER ####
    @abstractmethod
    def get_user(self, user_id: int) -> Tuple[Dict, int]:
        pass

    @abstractmethod
    def search_users(self, data: Dict[str, str]) -> Tuple[List[Dict], int]:
        """
        data fields:
        - email: string
        - telephone: string
        - ssn: string
        """
        pass

    @abstractmethod
    def get_users(self) -> Tuple[List[Dict], int]:
        pass

    @abstractmethod
    def _create_user(self, userdata: Dict) -> Tuple[Dict, int]:
        pass

    def create_user(self, userdata: Dict) -> Tuple[Dict, int]:
        userdata['password'] = generate_password_hash(userdata['password'])
        return self._create_user(userdata)

    def check_authenticate(self, user_id: int, password: str):
        user, status = self.get_user(user_id)
        if status != 200:
            return False
        else:
            return check_password_hash(user['password'], password)

    @abstractmethod
    def set_user_restaurant(self, user_id: int, rest_id: int) -> Tuple[Dict, int]:
        pass

    #### CONTACT TRACING ####

    @abstractmethod
    def get_positive_users(self) -> Tuple[List[Dict], int]:
        pass

    @abstractmethod
    def get_user_contacts(self, user_id: int, begin: str, end: str) -> Tuple[List[Dict], int]:
        pass

    @abstractmethod
    def mark_user(self, user_id: int) -> Tuple[Dict, int]:
        pass

    @abstractmethod
    def unmark_user(self, user_id: int) -> Tuple[Dict, int]:
        pass

    #### NOTIFICATIONS ####
    @abstractmethod
    def get_notifications(self, user_id: int, read: int = None) -> Tuple[List[Dict], int]:
        pass

    @abstractmethod
    def get_notification(self, notification_id: int) -> Tuple[Dict, int]:
        pass

    @abstractmethod
    def mark_notif_as_read(self, notification_id: int) -> Tuple[Dict, int]:
        pass

    #### RESTAURANTS ####
    @abstractmethod
    def get_restaurants(self, name: str, opening_time: int, open_day:int, cuisine_type:str, menu:str) -> Tuple[List[Dict], int]:
        pass
    
    @abstractmethod
    def post_restaurants(self, json: dict) -> Tuple[List[Dict], int]:
        pass

    @abstractmethod
    def get_restaurant(self, rest_id: int) -> Tuple[List[Dict], int]:
        pass

    @abstractmethod
    def edit_restaurant(self, rest_id: int, json: Dict) -> Tuple[List[Dict], int]:
        pass

    @abstractmethod
    def delete_restaurant(self, rest_id: int) -> Tuple[List[Dict], int]:
        pass

    @abstractmethod
    def get_restaurant_rate(self, rest_id: int) -> Tuple[List[Dict], int]:
        pass

    @abstractmethod
    def post_restaurant_rate(self, rest_id: int, rater_id: int, rating: int) -> Tuple[List[Dict], int]:
        pass

    #### TABLES ####
    def get_restaurants_tables(self,rest_id: int, capacity=None) -> Tuple[List[Dict], int]:
        pass
    
    def post_restaurants_tables(self,rest_id: int, capacity: int) -> Tuple[List[Dict], int]:
        pass

    def get_restaurants_table(self,rest_id: int, table_id: int) -> Tuple[List[Dict], int]:
        pass
    
    def edit_restaurants_table(self,rest_id: int, table_id: int, capacity: int) -> Tuple[List[Dict], int]:
        pass

    def delete_restaurants_table(self,rest_id: int, table_id: int) -> Tuple[List[Dict], int]:
        pass

    #### BOOKINGS ####

    @abstractmethod
    def get_bookings(self, user:int, rest:int, table:int, begin:str, end:str, begin_entrance:str, end_entrance:str, with_user:bool) -> Tuple[List[Dict], int]:
       pass

    @abstractmethod
    def get_a_booking(self, id:int, with_user:bool)  -> Tuple[Dict, int]:
        pass

    @abstractmethod
    def new_booking(self, user_id:int, rest_id:int, number_of_people:int, booking_datetime:str)  -> Tuple[Dict, int]:
        pass

    @abstractmethod
    def edit_booking(self, booking_id:int, number_of_people:int, booking_datetime:str, entrance:bool)  -> Tuple[Dict, int]:
        pass

    @abstractmethod
    def delete_booking(self, id:int) -> Tuple[Dict, int]:
        pass