"""
This module contains the views for the API endpoints related to routes.
"""
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.generics import GenericAPIView
from api.serializers import RouteSerializer
from ppf.common.models.route import Route


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
    - TODO: Notify the passenjers that the route was cancelled.
    - TODO: Issue a refund to the passenjers.
    - TBD

    URIs:
    - POST /routes/{id}/cancel
    """
    pass

class RouteJoinView(GenericAPIView):
    """
    Joins a passenjer to a route, this will:
    - Add the passenjer to the route.
    - Notify the driver that a passenjer joined the route.
    - Charge the passenjer the price of the route.
    - TBD

    URIs:
    - POST /routes/{id}/join
    """
    pass

class RouteLeaveView(GenericAPIView):
    """
    Leaves a passenjer from a route, this will:
    - Remove the passenjer from the route.
    - Notify the driver that a passenjer left the route.
    - Refund the passenjer the price of the route (conditions TBD)
    - TBD

    URIs:
    - POST /routes/{id}/leave
    """
    pass



class RouteFinishView(GenericAPIView):
    """
    Marks a route as finished, this will:
    - Set the route as finished.
    - Notify the passenjers that the route was finished.
    - Pay the driver the passenjers fees.
    - TBD

    URIs:
    - POST /routes/{id}/finish
    """
    pass

