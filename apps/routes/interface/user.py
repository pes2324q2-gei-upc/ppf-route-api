from abc import ABC, abstractmethod

from common.models.user import User


class UserService(ABC):
    @abstractmethod
    def getById(self, user: str) -> User:
        pass
