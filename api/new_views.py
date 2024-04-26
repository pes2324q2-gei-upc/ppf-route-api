from http.client import BAD_REQUEST

from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK


from api import ROUTE_CONTROLLER

RouteController = ROUTE_CONTROLLER  # alias
API_VERSION = "/v2"


class IncompatibleQueries(APIException):
    status_code = BAD_REQUEST
    default_detail = "Incompatible query params must especify either {a} or {b}"

    def __init__(self, a: str, b: str):
        self.default_detail = self.default_code.format(a, b)


class BaseRouteAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # renderer classes set by default in settings


class ListRoutes(BaseRouteAPIView):
    """
    This view allows to list routes and filter by the specified fields
    - Origin
    - Destination
    - Driver
    - Passenger
    - Number of free seats

    All fields accept one value and are ANDed
    """

    def get(self, request, format):
        # parse the query
        result = RouteController.findRouteByQuery(self.request.GET)
        return Response(result, HTTP_200_OK)
