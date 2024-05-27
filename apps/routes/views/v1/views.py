"""
This module contains the views for the API endpoints related to routes.
"""

from typing import Never, Union

from apps.routes.serializers.payments import PaymentMethodSerializer
from apps.routes.serializers.route import (
    CreateRouteSerializer,
    DetaliedRouteSerializer,
    ListRouteSerializer,
    PreviewRouteSerializer,
)
from common.models.achievement import *
from common.models.charger import *
from common.models.fcm import *
from common.models.payment import *
from common.models.route import *
from common.models.user import *
from common.models.valuation import *
from django.shortcuts import get_object_or_404
from django.urls import path
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ValidationError
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
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)
from rest_framework.views import APIView
from apps.routes import routesService


class RouteRetrieveView(RetrieveAPIView):
    """
    Returns a detalied view of a route
    URIs:
    - GET  /routes/{id}
    """

    authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    queryset = Route.objects.all()
    serializer_class = DetaliedRouteSerializer


from apps.routes import LatLon, computeRouteService, userService


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
            data={"driver": request.user.id, **request.data}  # type: ignore
        )
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        origin = LatLon(data.get("originLat"), data.get("originLon"))
        destination = LatLon(data.get("destinationLat"), data.get("destinationLon"))
        autonomy = userService.getDriverById(request.user.id).autonomy

        result = computeRouteService.computeChargingRoute(origin, destination, autonomy)

        return Response(result, status=HTTP_200_OK)


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

        driver = userService.getDriverById(request.user.id)

        serializer: CreateRouteSerializer = self.get_serializer(
            data={"driver": request.user.id, **request.data}  # type: ignore
        )
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        origin = LatLon(data.get("originLat"), data.get("originLon"))
        destination = LatLon(data.get("destinationLat"), data.get("destinationLon"))
        autonomy = userService.getDriverById(request.user.id).autonomy

        result = computeRouteService.computeChargingRoute(origin, destination, autonomy)

        instance = routesService.createRoute(driver=driver, **result)
        return Response(DetaliedRouteSerializer(instance).data, status=HTTP_201_CREATED)


class RouteValidateJoinView(APIView):
    # TODO breaking change, from GET to POST
    """
    Validate if a user can join a route
    URI:
    - GET /routes/{id}/validate_join
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: openapi.Response("User validated to join the route", {}),
        }
    )
    def get(self, request, *args, **kwargs):
        routeId = self.kwargs["pk"]
        userId = request.user.id
        validateJoinRoute(routeId, userId)
        return Response({"message": "User validated to join the route"}, status=HTTP_200_OK)


class RouteJoinView(CreateAPIView):
    """
    Join a route
    URI:
    - POST /routes/{id}/join
    """

    serializer_class = PaymentMethodSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        paymentMethodId = request.data.get("payment_method_id")
        routeId = self.kwargs["pk"]
        userId = request.user.id
        validateJoinRoute(routeId, userId)
        joinRoute(routeId, userId, paymentMethodId)

        route = Route.objects.get(id=routeId)
        notifyDriver(routeId, Notification.passengerJoined(route.destinationAlias))
        return Response({"message": "User successfully joined the route"}, status=HTTP_200_OK)


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

        route = Route.objects.get(id=routeId)
        notifyDriver(routeId, Notification.passengerLeft(route.destinationAlias))
        return Response({"message": "User successfully left the route"}, status=HTTP_200_OK)


class RouteCancelView(CreateAPIView):
    """
    Cancel a route
    URI:
    - POST /routes/{id}/cancel
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            route = Route.objects.get(id=self.kwargs["pk"])
        except Route.DoesNotExist:
            return Response({"message": "Route not exist"}, status=HTTP_404_NOT_FOUND)

        if route.driver_id != request.user.id:
            return Response(
                {"message": "You are not the driver of the route"}, status=HTTP_403_FORBIDDEN
            )

        if route.cancelled:
            return Response(
                {"message": "Route have been already cancelled"}, status=HTTP_400_BAD_REQUEST
            )

        if route.finalized:
            return Response(
                {"message": "Route have been already finalized"}, status=HTTP_400_BAD_REQUEST
            )

        for passenger in route.passengers.all():
            try:
                forcedLeaveRoute(route.id, passenger.id)
            except ValidationError as e:
                return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)

        route.cancelled = True
        route.save()
        notifyPassengers(route.id, Notification.routeCancelled(route.destinationAlias))
        return Response({"message": "Route successfully cancelled"}, status=HTTP_200_OK)


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


class FinishRoute(APIView):
    """
    End a route and save the changes to the database.

    Methods:
    - post(self, request, *args, **kwargs)
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        End a route and save the changes to the database.

        Parameters:
        - request (Request): The request object containing the current request data.
        - *args: Additional positional arguments.
        - **kwargs: Additional keyword arguments.

        Returns:
        - Response: The response object containing the serialized route data or an error message.
        """
        driver = get_object_or_404(Driver, pk=request.user.id)
        route = get_object_or_404(Route, pk=self.kwargs["pk"])
        if route.driver == driver:
            route.finalized = True
            route.save()
            serializer = DetaliedRouteSerializer(route)
            return Response(serializer.data, status=HTTP_200_OK)
        else:
            return Response(
                {"error": "You are not the driver of this route"}, status=HTTP_400_BAD_REQUEST
            )


urls = [
    path("routes", RouteListCreateView.as_view(), name="route-list-create"),
    path("routes/preview", RoutePreviewView.as_view(), name="route-list-create"),
    path("routes/<int:pk>", RouteRetrieveView.as_view(), name="route-detail"),
    path(
        "routes/<int:pk>/validate_join", RouteValidateJoinView.as_view(), name="route-validate-join"
    ),
    path("routes/<int:pk>/join", RouteJoinView.as_view(), name="route-join"),
    path("routes/<int:pk>/leave", RouteLeaveView.as_view(), name="route-leave"),
    path("routes/<int:pk>/passengers", RoutePassengersList.as_view(), name="route-list-passengers"),
    path("routes/<int:pk>/cancel", RouteCancelView.as_view(), name="route-cancel"),
    path("routes/<int:pk>/finish", FinishRoute.as_view(), name="route-finish"),
]
