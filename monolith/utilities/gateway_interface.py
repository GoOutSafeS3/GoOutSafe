from abc import ABC, abstractmethod
from werkzeug.security import check_password_hash, generate_password_hash
from typing import Tuple, Dict, List

class GatewayInterface(ABC):
    #### USER ####
    @classmethod
    @abstractmethod
    def get_user(self, user_id: int) -> Tuple[Dict, int]:
        pass

    @classmethod
    @abstractmethod
    def get_users(self) -> Tuple[List[Dict], int]:
        pass

    @classmethod
    @abstractmethod
    def _create_user(self, userdata: Dict) -> Tuple[Dict, int]:
        pass

    @classmethod
    def create_user(self, userdata: Dict):
        userdata['password'] = generate_password_hash(userdata['password'])
        return self._create_user(userdata)

    @classmethod
    def check_authenticate(self, user_id: int, password: str):
        user, status = self.get_user(user_id)
        if status != 200:
            return False
        else:
            return check_password_hash(user['password'], password)

    #### NOTIFICATIONS ####
    @classmethod
    @abstractmethod
    def get_notifications(self, user_id: int, read: int = None) -> Tuple[List[Dict], int]:
        pass

    @classmethod
    @abstractmethod
    def get_notification(self, notification_id: int) -> Tuple[Dict, int]:
        pass

    @classmethod
    @abstractmethod
    def mark_notif_as_read(self, notification_id: int) -> Tuple[Dict, int]:
        pass

    #### RESTAURANTS ####
    @classmethod
    @abstractmethod
    def get_restaurants(self) -> Tuple[List[Dict], int]:
        pass

    @classmethod
    @abstractmethod
    def get_restaurant(self, rest_id: int) -> Tuple[Dict, int]:
        pass

    @classmethod
    @abstractmethod
    def get_user_future_reservations(self, user_id: int) -> Tuple[List[Dict], int]:
        pass