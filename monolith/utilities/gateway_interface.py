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

    @abstractmethod
    def login_user(self, userdata: Dict) -> Tuple[Dict, int]:
        pass

    def check_authenticate(self, user_id: int, password: str):
        user, status = self.get_user(user_id)
        if status != 200:
            return False
        else:
            return check_password_hash(user['password'], password)

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
    def get_restaurants(self) -> Tuple[List[Dict], int]:
        pass

    @abstractmethod
    def get_restaurant(self, rest_id: int) -> Tuple[Dict, int]:
        pass

    @abstractmethod
    def get_user_future_reservations(self, user_id: int) -> Tuple[List[Dict], int]:
        pass

    #### RESERVATIONS ####
    @abstractmethod
    def get_reservation(self, reservation_id: int) -> Tuple[Dict, int]:
        pass

    @abstractmethod
    def delete_reservation(self, reservation_id: int) -> Tuple[Dict, int]:
        pass

    @abstractmethod
    def register_entrance(self, reservation_id: int) -> Tuple[Dict, int]:
        pass

    @abstractmethod
    def get_reservations(self, restaurant_id: int, begin: str, end: str) -> Tuple[List[Dict], int]:
        pass