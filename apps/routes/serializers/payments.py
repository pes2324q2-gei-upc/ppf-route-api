from rest_framework.serializers import Serializer
from rest_framework.serializers import CharField


class PaymentMethodSerializer(Serializer):
    payment_method_id = CharField()
