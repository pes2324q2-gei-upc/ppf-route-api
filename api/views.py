"""
This module contains the views for the API endpoints related to routes.
- TODO: See how exceptions are handled by the framework
"""

import logging
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.status import HTTP_200_OK
from api.serializers import RouteSerializer
from ppf.common.models.route import Route

from .service.route import *


class RouteListCreateView(ListCreateAPIView):
    """
    List and create routes.
    The route list will only contain a simplified version of all the active routes.
    URIs:
    - GET  /routes
    - POST /routes
    """

    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class RouteRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update and destroy routes by it's id.
    URIs:
    - GET  /routes/{id}
    - PUT  /routes/{id}
    """

    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class RouteCancelView(GenericAPIView):
    """
    Cancel a route, this will:
    - Set the route as cancelled.
    - Notify the passenjers that the route was cancelled.
    - Issue a refund to the passenjers.
    - TODO : TBD more actions

    URIs:
    - POST /routes/{id}/cancel
    """

    def post(self, request: Request, *args, **kwargs):
        routeId = request.data.get("routeId")

        # TBD determine what to do if this operations go wrong
        cancelRoute(routeId)  # Sync operation, TODO: RAISE EXCEPTION IF FAILS
        refundPassenjersFee(routeId)  # Async operation
        notifyRouteCancelled(routeId)  # Async operation

        return Response(status=HTTP_204_NO_CONTENT)


class RouteJoinView(GenericAPIView):
    """
    Joins a passenjer to a route, this will:
    - Add the passenjer to the route.
    - Notify the driver that a passenjer joined the route.
    - Charge the passenjer the price of the route.
    - TODO : TBD more actions

    URIs:
    - POST /routes/{id}/join
    """

    def post(self, request: Request, *args, **kwargs):
        logging.debug(f"{request}")
        logging.debug(f"{args}")
        logging.debug(f"{kwargs}")

        routeId = request.data.get("routeId")
        passenjerId = request.data.get("passenjerId")

        routePassenjerJoin(routeId, passenjerId)
        notifyPassenjerJoined(routeId, passenjerId)
        retainPassenjerFee(routeId, passenjerId)
        return Response(status=HTTP_200_OK)


class RouteLeaveView(GenericAPIView):
    """
    Leaves a passenjer from a route, this will:
    - Remove the passenjer from the route.
    - Notify the driver that a passenjer left the route.
    - Refund the passenjer the price of the route (conditions TBD)
    - TODO : TBD more actions

    URIs:
    - POST /routes/{id}/leave
    """

    def post(self, request: Request, *args, **kwargs):
        routeId = request.data.get("routeId")
        passenjerId = request.data.get("passenjerId")

        routePassenjerLeave(routeId, passenjerId)
        notifyPassenjerLeft(routeId, passenjerId)
        returnPassenjerFee(routeId, passenjerId)
        return Response(status=HTTP_200_OK)


class RouteFinishView(GenericAPIView):
    """
    Marks a route as finished, this will:
    - Set the route as finished.
    - Notify the passenjers that the route was finished.
    - Pay the driver the passenjers fees.
    - TODO : TBD more actions

    URIs:
    - POST /routes/{id}/finish
    """

    def post(self, request: Request, *args, **kwargs):
        routeId = request.data.get("routeId")
        driverId = request.data.get("driverId")

        finalizeRoute(routeId)
        notifyRouteFinished(routeId)
        payDriver(driverId)
        return Response(status=HTTP_200_OK)
