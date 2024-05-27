from os import read
from common.models.charger import (
    ChargerLocationType,
    ChargerVelocity,
    LocationCharger,
)
from rest_framework.serializers import ModelSerializer


class ConnectionTypeSerializer(ModelSerializer):
    class Meta:
        model = ChargerLocationType
        fields = ["chargerType"]


class ChargerVelocitySerializer(ModelSerializer):
    class Meta:
        model = ChargerVelocity
        fields = ["velocity"]


class LocationChargerSerializer(ModelSerializer):
    connectionType = ConnectionTypeSerializer(
        many=True,
        read_only=True,
    )
    velocities = ChargerVelocitySerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = LocationCharger
        fields = "__all__"
