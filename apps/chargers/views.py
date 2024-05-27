from apps.chargers import Licitation, chargerController, licitationService
from apps.chargers.serializers import LocationChargerSerializer
from common.models.achievement import *
from common.models.charger import *
from common.models.fcm import *
from common.models.payment import *
from common.models.route import *
from common.models.user import *
from common.models.valuation import *
from django.shortcuts import get_object_or_404
from django.urls import path
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from requests import HTTPError
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import APIException
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView


class ChargersView(ListAPIView):
    """
    Get the chargers around a latitude and longitude point with a radius
    Formula used to compute the distance between two points: Haversine formula
    For more computing precision:
        See GDAL library, django.contrib.gis.geos, django.contrib.gis.db.models.functions
    URI:
    - GET /chargers?latitud=&longitud=&radio_km=
    """

    serializer_class = LocationChargerSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("latitud", openapi.IN_QUERY, type=openapi.TYPE_NUMBER),
            openapi.Parameter("longitud", openapi.IN_QUERY, type=openapi.TYPE_NUMBER),
            openapi.Parameter("radio_km", openapi.IN_QUERY, type=openapi.TYPE_NUMBER),
        ]
    )
    def get_queryset(self):
        params = self.request.GET.dict()

        latitud = float(params.get("latitud"))  # type: ignore
        longitud = float(params.get("longitud"))  # type: ignore
        radio = float(params.get("radio_km"))  # type: ignore

        if not all([latitud, longitud, radio]):
            raise APIException("Missing parameters", code=HTTP_400_BAD_REQUEST)

        return chargerController.getByLocation(latitud, longitud, radio)


class ReportChargerView(APIView):
    """
    Create a new bid for a route using the charger Id
    URI:
    - POST /licitacion
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        charger = get_object_or_404(LocationCharger, pk=pk)
        licitation = Licitation(charger)

        try:
            licitationService.createLicitation(licitation)
        except HTTPError as e:
            raise APIException(f"Error creating the licitation", e.response.status_code)

        return Response({"message": "Error creating the licitacion"}, status=201)


urls = [
    path("chargers", ChargersView.as_view(), name="list-chargers"),
    path("chargers/<int:pk>/report", ReportChargerView.as_view(), name="charger-report"),
]
