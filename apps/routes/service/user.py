from django.shortcuts import get_object_or_404
from apps.routes.interface.user import UserService
from common.models.user import User


class DjangoUserService(UserService):
    manager = User.objects  # IDEA ie: could be changed so deleted users are not returned

    def getById(self, user: str) -> User:
        return get_object_or_404(self.manager, pk=user)
