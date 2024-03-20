from common.models.route import Route
from rest_framework.serializers import ModelSerializer, Serializer


class CreateRouteSerializer(ModelSerializer):
    class Meta:
        model = Route
        fields = [
            "driver",
            "originLat",
            "originLon",
            "originAlias",
            "destinationLat",
            "destinationLon",
            "destinationAlias",
            "departureTime",
            "freeSeats",
            "price",
        ]


class DetaliedRouteSerializer(ModelSerializer):
    class Meta:
        model = Route
        fields = "__all__"


class PreviewRouteSerializer(ModelSerializer):
    class Meta:
        model = Route
        fields = [
            "originLat",
            "originLon",
            "destinationLat",
            "destinationLon",
            "polyline",
            "duration",
            "distance",
        ]
        write_only_fields = [
            "originLat",
            "originLon",
            "destinationLat",
            "destinationLon",
        ]
        read_only_fields = [
            "polyline",
            "duration",
            "distance",
        ]


class ListRouteSerializer(ModelSerializer):
    class Meta:
        model = Route
        fields = [
            "id",
            "driver",
            "originAlias",
            "destinationAlias",
            "distance",
            "duration",
            "departureTime",
            "freeSeats",
            "price",
        ]


# The following fields are available in the Route model:
# "id"
# "driver"
# "originLat"
# "originLon"
# "originAlias"
# "destinationLat"
# "destinationLon"
# "destinationAlias"
# "polyline"
# "distance"
# "duration"
# "departureTime"
# "freeSeats"
# "price"
# "cancelled"
# "finalized"
# "createdAt"
