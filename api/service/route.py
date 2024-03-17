from time import sleep
from api import GoogleMapsRouteClient
from google.maps.routing_v2 import ComputeRoutesRequest, ComputeRoutesResponse, Location
from google.maps.routing_v2 import Route as GRoute
from typing import Union

from api.serializers import PreviewRouteSerializer, RouteSerializer

X_GOOGLE_FIELDS = (
    "x-goog-fieldmask",
    "routes.distanceMeters,routes.duration,routes.polyline.encodedPolyline",
)


def buildMapsRouteRequest(serializer: Union[PreviewRouteSerializer]) -> ComputeRoutesRequest:
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


def computeMapsRoute(serializer: Union[PreviewRouteSerializer, RouteSerializer]):
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
