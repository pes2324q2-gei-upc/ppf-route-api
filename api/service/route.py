from typing import Union

from common.models.payment import Payment
from django.utils import timezone
import requests
import json
from api import GoogleMapsRouteClient
from api.serializers import CreateRouteSerializer, PreviewRouteSerializer
from common.models.route import Route
from common.models.user import User
from common.models.valuation import Valuation  # Dont remove, it is use for migrate well
from google.maps.routing_v2 import ComputeRoutesRequest, ComputeRoutesResponse
from google.maps.routing_v2 import Route as GRoute
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

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
                    "latitude": serializer.validated_data.get("originLat"),  # type: ignore
                    "longitude": serializer.validated_data.get("originLon"),  # type: ignore
                }
            }
        },
        "destination": {
            "location": {
                "lat_lng": {
                    "latitude": serializer.validated_data.get("destinationLat"),  # type: ignore
                    "longitude": serializer.validated_data.get("destinationLon"),  # type: ignore
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


def validateJoinRoute(routeId: int, passengerId: int):
    """
    Validates if a user can join a route.

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

    if route.cancelled:
        raise ValidationError("You can not join a cancelled route", 400)

    if route.finalized:
        raise ValidationError("You can not join a finalized route", 400)

    # check if the user is already in a route that overlaps with the current route
    joinedRoutes = route.passengers.filter(id=passengerId)
    for joinedRoute in joinedRoutes:
        if route.overlapsWith(joinedRoute.route):
            raise ValidationError(
                "User is already in a route that overlaps with the current route", 400
            )


def joinRoute(routeId: int, passengerId: int, paymentMethodId: str):
    """
    Joins a user to a route after payment is successfull.

    Args:
        route_id (int): The ID of the route.
        user_id (int): The ID of the user.
    """
    try:
        route = Route.objects.get(id=routeId)
    except Route.DoesNotExist:
        raise ValidationError("Route does not exist", 400)

    try:
        token = Token.objects.get(user_id=passengerId)
    except Token.DoesNotExist:
        raise ValidationError("User does not have a token", 400)

    url = "http://payments-api:8000/process_payment/"
    data = {
        "payment_method_id": paymentMethodId,
        "route_id": routeId,
    }
    headers = {"Content-Type": "application/json", "Authorization": "Token " + token.key}
    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code != 200:
        raise ValidationError("Payment failed and user did not join the route", 400)

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

    # Only refund if more than 24 hours before the departure time
    if (route.departureTime - timezone.now()).days >= 1:
        try:
            token = Token.objects.get(user_id=passengerId)
        except Token.DoesNotExist:
            raise ValidationError("User does not have a token", 400)

        url = "http://payments-api:8000/refund/"
        data = {
            "route_id": routeId,
        }
        headers = {"Content-Type": "application/json", "Authorization": "Token " + token.key}
        response = requests.post(url, data=json.dumps(data), headers=headers)

        if response.status_code != 200:
            raise ValidationError("Refund failed and User did not leave the route", 400)

    route.passengers.remove(User.objects.get(id=passengerId))


def forcedLeaveRoute(routeId: int, passengerId: int):
    """
    Forces a user to leave a route.

    Args:
        route_id (int): The ID of the route.
        user_id (int): The ID of the user.
    """
    route = Route.objects.get(id=routeId)
    if not route.passengers.filter(id=passengerId).exists():
        raise ValidationError("User is not in the route", 400)

    try:
        token = Token.objects.get(user_id=passengerId)
    except Token.DoesNotExist:
        raise ValidationError("User does not have a token", 400)

    url = "http://payments-api:8000/refund/"
    data = {
        "route_id": routeId,
    }
    headers = {"Content-Type": "application/json", "Authorization": "Token " + token.key}
    requests.post(url, data=json.dumps(data), headers=headers)

    # If refund fails, user is still removed from the route.
    # Contact us by email to resolve the issue.
    route.passengers.remove(User.objects.get(id=passengerId))
