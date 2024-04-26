from api.serializers import ListRouteSerializer
from api.service.route_controller import RouteController
from api.service.route_filters import BaseRouteFilter
from drf_yasg.openapi import IN_QUERY, TYPE_ARRAY, Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

routeController = RouteController()  # alias

# Got from RouteManager to avoid having Models used in views, errase if having models is inevitable
# and change it to Route.objects or Route.default_manager (whatever works)
routeManager = routeController.routeManager
API_VERSION = "/v2"


class BaseRouteAPIView(APIView):
    """
    Routes service can only be accesed by authenticated and authorized users
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # renderer classes set by default in settings


class ListRoutes(BaseRouteAPIView, ListAPIView):
    """
    Retrieves a list of routes
    TODO Complete description
    """

    serializer_class = ListRouteSerializer
    filterset_class = BaseRouteFilter

    def get_queryset(self):
        # the query set is retrieved from the "domain"
        # we get all the active routes and chain querysets
        # depending on the url query param 'include'
        qset = routeManager.active()
        for value in self.request.GET.getlist("include", []):
            if value == "cancelled":
                qset = qset | routeManager.cancelled()
            if value == "finalized":
                qset = qset | routeManager.finalized()
        return qset

    @swagger_auto_schema(  # TODO refactor to it's own file if multiple manual params are specified
        manual_parameters=[
            Parameter(
                "include",
                IN_QUERY,
                description="Stablish if non active routes should be included",
                items=["cancelled", "finalized"],  # this does not work
                type=TYPE_ARRAY,
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        # Filtering and pagination happen at 'view level' (whatever that means)
        return super().get(request, *args, **kwargs)
