from common.models.route import Route
from rest_framework.serializers import Serializer, ModelSerializer, CharField

from common.models.user import User
from common.models.charger import LocationCharger, ChargerLocationType, ChargerVelocity


class PaymentMethodSerializer(Serializer):
    class ChargerVelocitySerializer(ModelSerializer):
        class Meta:
            model = ChargerVelocity
            fields = ["velocity"]

    class ConnectionTypeSerializer(ModelSerializer):
        class Meta:
            model = ChargerLocationType
            fields = ["chargerType"]

    payment_method_id = CharField()
