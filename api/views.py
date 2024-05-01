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
    LocationChargerSerializer,
)
from common.models.route import Route
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import (
    CreateAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    ListAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
)

from common.models.user import Driver
from .service.route import computeMapsRoute, joinRoute, leaveRoute


from common.models.charger import LocationCharger


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
        serializer = self.get_serializer(data={"driver": request.user.id, **request.data})  # type: ignore

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


from math import radians, cos, sin, sqrt, atan2


class NearbyChargersView(ListAPIView):
    """
    Get the chargers around a latitude and longitude point with a radius
    URI:
    - GET /nearby-chargers?latitud=0&longitud=0&radio=0
    """

    serializer_class = LocationChargerSerializer

    def get_queryset(self):
        latitud = float(self.request.query_params.get("latitud"))  # type: ignore
        longitud = float(self.request.query_params.get("longitud"))  # type: ignore
        radio = float(self.request.query_params.get("radio")) * 1000  # type: ignore    # Change to meters

        """
        central_point = Point(longitud, latitud, srid=4326)
        central_point.transform(25831)

        # Calculate the distance between the point and the chargers in the database (more
        # efficient than calculating it in the code)
        queryset = LocationCharger.objects.annotate(
            transform_point=Transform(Point(F("longitud"), F("latitud"), srid=4326), 25831),
            distancia=Distance("transform_point", central_point),
        ).filter(distancia__lte=radio)

        return queryset"""

        if latitud and longitud and radio:
            queryset = LocationCharger.objects.all()
            cargadores_cercanos = []

            for cargador in queryset:
                # Convertir a radianes
                lat1, lon1, lat2, lon2 = map(
                    radians, [latitud, longitud, cargador.latitud, cargador.longitud]
                )

                # Fórmula del haversine
                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
                c = 2 * atan2(sqrt(a), sqrt(1 - a))
                distancia = 6371 * c  # Radio de la Tierra en km

                if distancia <= radio:
                    cargadores_cercanos.append(cargador)

            return cargadores_cercanos

        return LocationCharger.objects.none()
