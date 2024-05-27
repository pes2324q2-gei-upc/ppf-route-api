from django.shortcuts import get_object_or_404
from apps.routes.interface.user import UserService
from common.models.user import Driver, User


class DjangoUserService(UserService):
    userManager = User.objects  # IDEA ie: could be changed so deleted users are not returned
    driverManager = Driver.objects

    def getById(self, user: str) -> User:
        return get_object_or_404(self.userManager, pk=user)

    def getDriverById(self, driver: str) -> Driver:
        return get_object_or_404(self.driverManager, pk=driver)
