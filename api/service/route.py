from typing import Union

from api import GoogleMapsRouteClient
from api.serializers import CreateRouteSerializer, PreviewRouteSerializer
from common.models.route import Route
from common.models.user import User
from common.models.valuation import Valuation # Dont remove, it is use for migrate well
from google.maps.routing_v2 import ComputeRoutesRequest, ComputeRoutesResponse
from google.maps.routing_v2 import Route as GRoute
from rest_framework.exceptions import ValidationError

X_GOOGLE_FIELDS = (
    "x-goog-fieldmask",
    "routes.distanceMeters,routes.duration,routes.polyline.encodedPolyline",
)


def buildMapsRouteRequest(
    serializer: Union[PreviewRouteSerializer, CreateRouteSerializer]
) -> ComputeRoutesRequest:
    """
    Creates a ComputeRoutesRequest object based on the passed data.

    Returns:
        ComputeRoutesRequest: The created ComputeRoutesRequest object.
    """
    mapping = {
        "origin": {
            "location": {
                "lat_lng": {
                    "latitude": serializer.data.get("originLat"),
                    "longitude": serializer.data.get("originLon"),
                }
            }
        },
        "destination": {
            "location": {
                "lat_lng": {
                    "latitude": serializer.data.get("destinationLat"),
                    "longitude": serializer.data.get("destinationLon"),
                }
            }
        },
    }
    computeRoutesRequest = ComputeRoutesRequest(mapping)
    return computeRoutesRequest


def deserializeMapsRoutesResponse(mapsRoute: ComputeRoutesResponse):
    """
    Derializes a ComputeRoutesResponse object into the serializer.

    Args:
        response (ComputeRoutesResponse): The ComputeRoutesResponse object to serialize.
    """
    assert isinstance(mapsRoute, ComputeRoutesResponse), "Wrong type for response parameter"

    if not mapsRoute.routes:
        raise ValueError("No routes found")

    route: GRoute = mapsRoute.routes[0]
    return {
        "polyline": route.polyline.encoded_polyline,
        "duration": route.duration.seconds,
        "distance": route.distance_meters,
    }


def computeMapsRoute(serializer: Union[PreviewRouteSerializer, CreateRouteSerializer]):
    """
    Computes the route using the Google Maps API based on the provided serializer.

    Args:
        serializer (Union[CreatePreviewRouteSerializer, CreateRouteSerializer]): The serializer object containing the route information.

    Returns:
        The deserialized response from the Google Maps API.
    """
    mapsPayload = buildMapsRouteRequest(serializer)

    # Initialize request argument(s)
    request = ComputeRoutesRequest(mapping=mapsPayload)
    response = GoogleMapsRouteClient.compute_routes(request=request, metadata=[X_GOOGLE_FIELDS])

    # Deserialize the response from the Google Maps API and send it back to the client
    return deserializeMapsRoutesResponse(response)


def joinRoute(routeId: int, passengerId: int):
    """
    Joins a user to a route.

    Args:
        route_id (int): The ID of the route.
        user_id (int): The ID of the user.
    """
    route = Route.objects.get(id=routeId)
    if route.driver.pk == passengerId:
        raise ValidationError("Driver can't join the route", 400)

    if route.isFull():
        raise ValidationError("Route is full", 400)

    if route.passengers.filter(id=passengerId).exists():
        raise ValidationError("User is already in the route", 400)

    # check if the user is already in a route that overlaps with the current route
    joinedRoutes = route.passengers.filter(id=passengerId)
    for joinedRoute in joinedRoutes:
        if route.overlapsWith(joinedRoute.route):
            raise ValidationError(
                "User is already in a route that overlaps with the current route", 400
            )
    passenger = User.objects.get(id=passengerId)
    route.passengers.add(passenger)


def leaveRoute(routeId: int, passengerId: int):
    """
    Leaves a user from a route.

    Args:
        route_id (int): The ID of the route.
        user_id (int): The ID of the user.
    """
    route = Route.objects.get(id=routeId)
    if not route.passengers.filter(id=passengerId).exists():
        raise ValidationError("User is not in the route", 400)
    route.passengers.filter(id=passengerId).delete()
