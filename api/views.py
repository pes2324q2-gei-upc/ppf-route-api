"""
This module contains the views for the API endpoints related to routes.
- TODO: See how exceptions are handled by the framework
"""

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.generics import RetrieveAPIView, ListCreateAPIView, CreateAPIView
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .service.route import computeMapsRoute
from common.models.route import Route
from api.serializers import (
    CreateRouteSerializer,
    PreviewRouteSerializer,
    DetaliedRouteSerializer,
    ListRouteSerializer,
)


class RouteRetrieveView(RetrieveAPIView):
    """
    Returns a detalied view of a route
    URIs:
    - GET  /routes/{id}
    """

    queryset = Route.objects.all()
    serializer_class = DetaliedRouteSerializer


class RoutePreviewView(CreateAPIView):
    """
    Returns a preview of a route.
    URI:
    - POST /routes/preview
    """

    serializer_class = PreviewRouteSerializer

    def post(self, request: Request, *args, **kargs):
        serializer = self.get_serializer(data=request.data)

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

    def get_queryset(self):
        return Route.objects.filter(cancelled=False)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateRouteSerializer
        return ListRouteSerializer

    @swagger_auto_schema(
        responses={
            201: openapi.Response("Route created", DetaliedRouteSerializer),
        }
    )
    def post(self, request: Request, *args, **kargs):
        # TODO search for a cached route to not duplicate the route request to maps api

        serializer: CreateRouteSerializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=HTTP_400_BAD_REQUEST)

        # Transform the recieved data into a format that the Google Maps API can understand and send the request
        mapsResponseData = computeMapsRoute(serializer)

        # We need both the data from google maps and the data from the original request to create the route
        completeSerializer = DetaliedRouteSerializer(data={**serializer.data, **mapsResponseData})

        if not completeSerializer.is_valid():
            return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)
        completeSerializer.save()
        return Response(completeSerializer.data, status=HTTP_201_CREATED)
