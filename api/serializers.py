from common.models.route import Route
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from common.models.user import User, GoogleCalendarCredentials
from common.models.charger import LocationCharger, ChargerLocationType, ChargerVelocity


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
        class Meta:
            model = User
            fields = ["id", "username"]

    driver = UserListSerializer(many=False, read_only=True)
    passengers = UserListSerializer(many=True, read_only=True)
    originDistance = serializers.FloatField(read_only=True, required=False)
    destinationDistance = serializers.FloatField(read_only=True, required=False)

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
            "originDistance",
            "destinationDistance",
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


class ChargerVelocitySerializer(ModelSerializer):
    class Meta:
        model = ChargerVelocity
        fields = ["velocity"]


class ConnectionTypeSerializer(ModelSerializer):
    class Meta:
        model = ChargerLocationType
        fields = ["chargerType"]


class LocationChargerSerializer(ModelSerializer):
    connectionType = ConnectionTypeSerializer(many=True)
    velocities = ChargerVelocitySerializer(many=True)

    class Meta:
        model = LocationCharger
        fields = [
            "promotorGestor",
            "access",
            "connectionType",
            "kw",
            "acDc",
            "velocities",
            "latitud",
            "longitud",
            "adreA",
        ]


class PaymentMethodSerializer(serializers.Serializer):
    payment_method_id = serializers.CharField()


class CalendarTokenSerializer(ModelSerializer):
    class Meta:
        model = GoogleCalendarCredentials
        fields = [
            "access_token",
            "refresh_token",
            "token_expiry",
        ]

    def create(self, validated_data):
        user = self.context["request"].user

        try:
            credentials = GoogleCalendarCredentials.objects.get(user=user)
            credentials.access_token = validated_data.get("access_token", credentials.access_token)
            credentials.refresh_token = validated_data.get(
                "refresh_token", credentials.refresh_token
            )
            credentials.token_expiry = validated_data.get("token_expiry", credentials.token_expiry)
            credentials.save()
            return credentials
        except GoogleCalendarCredentials.DoesNotExist:
            # No deja crear el modelo con el request.user
            userModel = User.objects.get(id=user.id)
            return GoogleCalendarCredentials.objects.create(user=userModel, **validated_data)
