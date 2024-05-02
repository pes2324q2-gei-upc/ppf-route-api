"""
This module contains the views for the API endpoints related to routes.
- TODO: See how exceptions are handled by the framework
"""

from typing import Union
from api.serializers import (
    CreateRouteSerializer,
    DetaliedRouteSerializer,
    ListRouteSerializer,
    PreviewRouteSerializer,
    UserSerializer,
)
from common.models.route import Route
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import (
    CreateAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from common.models.user import Driver
from .service.route import computeMapsRoute, joinRoute, leaveRoute
# Don't delete, needed to create db with models
from common.models.charger import ChargerLocationType, ChargerVelocity, ChargerLocationType


class RouteRetrieveView(RetrieveAPIView):
    """
    Returns a detalied view of a route
    URIs:
    - GET  /routes/{id}
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Route.objects.all()
    serializer_class = DetaliedRouteSerializer


class RoutePreviewView(CreateAPIView):
    """
    Returns a preview of a route.
    URI:
    - POST /routes/preview
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PreviewRouteSerializer

    def post(self, request: Request, *args, **kargs):
        serializer = self.get_serializer(
            data={"driver": request.user.id, **request.data})  # type: ignore

        if not serializer.is_valid(raise_exception=True):
            return Response(status=HTTP_400_BAD_REQUEST)

        # Compute the route and return it
        preview = computeMapsRoute(serializer)

        # TODO cache the route, maybe use a hash of the coordinates as the key

        return Response(preview, status=HTTP_200_OK)


class RouteListCreateView(ListCreateAPIView):
    """
    List and create routes.
    When creating a route, if the preview parameter is set to true, the route will not be saved in the
    database.
    URIs:
    - GET  /routes
    - POST /routes
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Route.objects.filter(cancelled=False)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateRouteSerializer
        return ListRouteSerializer

    def get_serializer(self, *args, **kwargs) -> Union[CreateRouteSerializer, ListRouteSerializer]:
        return super().get_serializer(*args, **kwargs)

    @swagger_auto_schema(
        responses={
            201: openapi.Response("Route created", DetaliedRouteSerializer),
        }
    )
    def post(self, request: Request, *args, **kargs):
        # TODO search for a cached route to not duplicate the route request to maps api
        driver = Driver.objects.get(id=request.user.id)

        serializer: CreateRouteSerializer = self.get_serializer(
            data={**request.data, "driver": request.user.id}  # type: ignore
        )
        if not serializer.is_valid():
            return Response(status=HTTP_400_BAD_REQUEST)

        # Transform the recieved data into a format that the Google Maps API can understand and send the request
        mapsResponseData = computeMapsRoute(serializer)
        serializer.save(**{**mapsResponseData, "driver_id": request.user.id})

        return Response(serializer.data, status=HTTP_201_CREATED)


class RouteJoinView(CreateAPIView):
    """
    Join a route
    URI:
    - POST /routes/{id}/join
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        routeId = self.kwargs["pk"]
        userId = request.user.id
        joinRoute(routeId, userId)
        return Response(status=HTTP_200_OK)


class RouteLeaveView(CreateAPIView):
    """
    Leave a route
    URI:
    - POST /routes/{id}/leave
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        routeId = self.kwargs["pk"]
        userId = request.user.id
        leaveRoute(routeId, userId)
        return Response(status=HTTP_200_OK)


class RouteCancellView(CreateAPIView):
    """
    Join a route
    URI:
    - POST /routes/{id}/cancell
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Route.objects.all()


class RoutePassengersList(RetrieveAPIView):
    """
    Get the passengers of a route
    URI:
    - GET /routes/{id}/passengers
    """

    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        route_id = self.kwargs["pk"]
        route = Route.objects.get(id=route_id)
        passengers = route.passengers.all()
        serializer = self.get_serializer(passengers, many=True)
        return Response(serializer.data)
