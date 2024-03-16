from typing import Never
from google.maps.routing_v2 import RoutesClient, ComputeRoutesRequest, ComputeRoutesResponse


from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import Serializer
from rest_framework.serializers import CharField, FloatField

from ppf.common.models.route import Route
from google.maps.routing_v2 import Route as GRoute


class RouteSerializer(ModelSerializer):

    class Meta:
        model = Route
        fields = "__all__"

    def mapsRouteRequest(self) -> ComputeRoutesRequest:
        """
        Creates a ComputeRoutesRequest object based on the serialized data.

        Returns:
            ComputeRoutesRequest: The created ComputeRoutesRequest object.
        """
        assert not self.is_valid(), "Can't create a ComputeRoutesRequest from an invalid serializer"

        computeRoutesRequest = ComputeRoutesRequest()
        computeRoutesRequest.origin = {
            "location": {
                "latLng": {
                    "latitude": self.data.get("originLat"),
                    "longitude": self.data.get("originLon"),
                }
            }
        }
        computeRoutesRequest.destination = {
            "location": {
                "latLng": {
                    "latitude": self.data.get("destinationLat"),
                    "longitude": self.data.get("destinationLon"),
                }
            }
        }
        return computeRoutesRequest

    @staticmethod
    def deserializeComputeRoutesResponse(self, response: ComputeRoutesResponse) -> dict:
        """
        Serializes a ComputeRoutesResponse object into the serializer.

        Args:
            response (ComputeRoutesResponse): The ComputeRoutesResponse object to serialize.

        Returns:
            Never: This method never returns.
        """
        assert isinstance(response, ComputeRoutesResponse), "Wrong type for response parameter"

        route: GRoute = response.routes[0]
        return {
            "originLat": route.origin.location.latLng.latitude,
            "originLon": route.origin.location.latLng.longitude,
            "destinationLat": route.destination.location.latLng.latitude,
            "destinationLon": route.destination.location.latLng.longitude,
            "polyline": route.polyline,
            "duration": route.duration,
            "departureTime": route.departureTime,
        }


class PreviewRouteSerializer(RouteSerializer):
    class Meta:
        model = Route
        fields = [
            "originLat",
            "originLon",
            "destinationLat",
            "destinationLon",
            "polyline",
            "duration",
            "departureTime",
        ]
        extra_kwargs = {
            "polyline": {"required": False},
            "duration": {"required": False},
            "departureTime": {"required": False},
        }
