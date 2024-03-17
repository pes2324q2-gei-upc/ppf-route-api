"""
This module contains the views for the API endpoints related to routes.
- TODO: See how exceptions are handled by the framework
"""

from rest_framework.generics import RetrieveAPIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.status import HTTP_200_OK
from rest_framework.status import HTTP_201_CREATED

from rest_framework.exceptions import ValidationError
from api.serializers import PreviewRouteSerializer, RouteSerializer
from ppf.common.models.route import Route

from .service.route import *
from .service.route import computeMapsRoute
from . import GoogleMapsRouteClient


class RouteListCreateView(ListCreateAPIView):
    """
    List and create routes.
    When creating a route, if the preview parameter is set to true, the route will not be saved in the
    database.
    URIs:
    - GET  /routes
    - POST /routes
    """

    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def post(self, request: Request, *args, **kwargs):
        preview: bool = request.data.get("preview")
        data: dict = request.data.get("route")

        if preview:
            routeSerializer = PreviewRouteSerializer(data=data)
        else:
            routeSerializer = RouteSerializer(data=data)

        if not routeSerializer.is_valid():
            raise ValidationError("Invalid request body")

        # Transform the recieved data into a format that the Google Maps API can understand and send the request
        mapsPayload = routeSerializer.mapsRouteRequest()
        mapsRoute = computeMapsRoute(mapsPayload, GoogleMapsRouteClient)

        # Deserialize the response from the Google Maps API and send it back to the client
        computeRoutesResponseData: dict = RouteSerializer.deserializeComputeRoutesResponse(preview, mapsRoute)

        # Once we have the google maps data
        # If it's a preview, we just return the data, if not, we create the route and return the data
        if preview:
            computeRoutesResponseData.pop()
            return Response(computeRoutesResponseData, status=HTTP_200_OK)

        # We need both the data from google maps and the data from the original request to create the route
        complete = {**data, **computeRoutesResponseData}
        routeSerializer = RouteSerializer(data=complete)
        routeSerializer.is_valid(raise_exception=True)
        routeSerializer.create()

        return Response(routeSerializer.data, status=HTTP_201_CREATED)


class RouteRetrieveView(RetrieveAPIView):
    """
    Retrieve, update and destroy routes by it's id.
    URIs:
    - GET  /routes/{id}
    """

    queryset = Route.objects.all()
    serializer_class = RouteSerializer
