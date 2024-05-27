from abc import ABC, abstractmethod

from common.models.user import Driver, User


class UserService(ABC):
    @abstractmethod
    def getById(self, user: str) -> User:
        pass

    @abstractmethod
    def getDriverById(self, driver: str) -> Driver:
        pass
