from os import read
from common.models.route import Route
from rest_framework.serializers import ModelSerializer

from common.models.user import User


class CreateRouteSerializer(ModelSerializer):
    class Meta:
        model = Route
        fields = [
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


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class DetaliedRouteSerializer(ModelSerializer):
    passengers = UserSerializer(many=True, read_only=True)
    driver = UserSerializer(read_only=True)

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
    class UserListSerializer(ModelSerializer):
      driver = UserListSerializer(many=False, read_only=True)
      passengers = UserListSerializer(many=True, read_only=True)
        class Meta:
            model = User
            fields = ["id", "username"]

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
            "passengers",
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
