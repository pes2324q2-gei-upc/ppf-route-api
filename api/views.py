"""
This module contains the views for the API endpoints related to routes.
"""

from math import atan2, cos, radians, sin, sqrt
from typing import Union

from django.shortcuts import get_object_or_404
import requests
from api.serializers import (
    CreateRouteSerializer,
    DetaliedRouteSerializer,
    ListRouteSerializer,
    LocationChargerSerializer,
    PaymentMethodSerializer,
    PreviewRouteSerializer,
    UserSerializer,
)

from common.models.achievement import *
from common.models.charger import *
from common.models.fcm import *
from common.models.payment import *
from common.models.route import *
from common.models.user import *
from common.models.valuation import *
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
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
    HTTP_409_CONFLICT,
)

from .service.route import (
    computeMapsRoute,
    computeOptimizedRoute,
    forcedLeaveRoute,
    joinRoute,
    leaveRoute,
    validateJoinRoute,
    forcedLeaveRoute,
)
from .service.notify import Notification, notifyDriver, notifyPassengers

from .service.licitacio import serializeLicitacio

# Don't delete, needed to create db with models
from common.models.charger import ChargerLocationType, ChargerVelocity, ChargerLocationType
from common.models.achievement import Achievement, UserAchievementProgress

from math import radians, cos, sin, sqrt, atan2
from common.models.charger import LocationCharger


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

        if not serializer.is_valid(raise_exception=True):
            return Response(status=HTTP_400_BAD_REQUEST)

        # Compute the route and return it
        routeData, waypoints = computeOptimizedRoute(
            serializer, request.user.id)

        return Response({**routeData, "waypoints": waypoints}, status=HTTP_200_OK)


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
        routeData, waypoints = computeOptimizedRoute(serializer, driver.pk)

        # Create the route in the database by validating first the route data
        instance: Route = serializer.save(
            driver=driver,
            waypoints=waypoints,
            **routeData,
        )
        return Response(DetaliedRouteSerializer(instance).data, status=HTTP_201_CREATED)


class RouteValidateJoinView(CreateAPIView):
    """
    Validate if a user can join a route
    URI:
    - POST /routes/{id}/validate_join
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        routeId = self.kwargs["pk"]
        userId = request.user.id
        validateJoinRoute(routeId, userId)
        return Response(
            {"message": "User successfully validated to join the route"}, status=HTTP_200_OK
        )


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


class NearbyChargersView(ListAPIView):
    """
    Get the chargers around a latitude and longitude point with a radius
    Formula used to compute the distance between two points: Haversine formula
    For more computing precision:
        See GDAL library, django.contrib.gis.geos, django.contrib.gis.db.models.functions
    URI:
    - GET /chargers?latitud=&longitud=&radio_km=
    """

    serializer_class = LocationChargerSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("latitud", openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER),
            openapi.Parameter("longitud", openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER),
            openapi.Parameter("radio_km", openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER),
        ]
    )
    def get(self, request, *args, **kwargs):
        params = request.GET.dict()
        latitud = params.get("latitud", None)
        longitud = params.get("longitud", None)
        radio = params.get("radio_km", None)

        if not all([latitud, longitud, radio]):
            return Response(
                {"error": "Missing parameters: latitud, longitud or radio_km"},
                status=HTTP_400_BAD_REQUEST,
            )

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        params = self.request.GET.dict()
        # get_queryset is called just if three parameters are provided
        latitud = float(params.get("latitud"))  # type: ignore
        longitud = float(params.get("longitud"))  # type: ignore
        radio = float(params.get("radio_km"))  # type: ignore

        queryset = LocationCharger.objects.all()
        cargadores_cercanos = []

        for cargador in queryset:
            # TODO can we get this out of the controller?
            # Apply the haversine formula to calculate the distance between two points
            lat1, lon1, lat2, lon2 = map(
                radians, [latitud, longitud,
                          cargador.latitud, cargador.longitud]
            )
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distancia = 6371 * c  # Radio of the Earth in km

            # If the charger is within the radius, add it to the list
            if distancia <= radio:
                cargadores_cercanos.append(cargador)

        return cargadores_cercanos


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


class LicitacioService(CreateAPIView):
    """
    Create a new bid for a route using the charger Id
    URI:
    - POST /licitacion
    """

    def post(self, request, pk, *args, **kwargs):
        url = "https://licitapp-back-f4zi3ert5q-oa.a.run.app/licitacions/licitacio"
        charger = get_object_or_404(LocationCharger, pk=pk)
        data = serializeLicitacio(charger)
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 201:
            return Response({"message": "Licitacion created successfully"}, status=HTTP_201_CREATED)

        else:
            return Response({"message": "Error creating the licitacion"}, status=response.status_code)
