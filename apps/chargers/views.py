"""
This module contains the views for the API endpoints related to routes.
"""

import os
from math import atan2, cos, radians, sin, sqrt

import requests
from api.serializers import LocationChargerSerializer
from common.models.achievement import *
from common.models.charger import *
from common.models.charger import LocationCharger
from common.models.fcm import *
from common.models.payment import *
from common.models.route import *
from common.models.user import *
from common.models.valuation import *
from django.shortcuts import get_object_or_404
from django.urls import path
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView


class NearbyChargersView(ListAPIView):
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
    def get(self, request, *args, **kwargs):
        params = request.GET.dict()
        latitud = params.get("latitud", None)
        longitud = params.get("longitud", None)
        radio = params.get("radio_km", None)

        if not all([latitud, longitud, radio]):
            return Response(
                {"error": "Missing parameters: latitud, longitud or radio_km"},
                status=HTTP_400_BAD_REQUEST,
            )

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        params = self.request.GET.dict()
        # get_queryset is called just if three parameters are provided

        latitud = float(params.get("latitud"))  # type: ignore
        longitud = float(params.get("longitud"))  # type: ignore
        radio = float(params.get("radio_km"))  # type: ignore

        queryset = LocationCharger.objects.all()
        cargadores_cercanos = []

        for cargador in queryset:
            # TODO can we get this out of the controller?
            # Apply the haversine formula to calculate the distance between two points
            lat1, lon1, lat2, lon2 = map(
                radians, [latitud, longitud, cargador.latitud, cargador.longitud]
            )
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distancia = 6371 * c  # Radio of the Earth in km

            # If the charger is within the radius, add it to the list
            if distancia <= radio:
                cargadores_cercanos.append(cargador)

        return cargadores_cercanos


LICITAPP_URL = os.environ.get(
    "LICITAPP_URL", "https://licitapp-back-f4zi3ert5q-oa.a.run.app/licitacions/licitacio"
)


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

        data = serializeLicitacio(charger)
        headers = {"Content-Type": "application/json"}
        response = requests.post(LICITAPP_URL, json=data, headers=headers)

        if response.status_code == 201:
            return Response({"message": "Licitacion created successfully"}, status=HTTP_201_CREATED)

        else:
            return Response(
                {"message": "Error creating the licitacion"}, status=response.status_code
            )


urls = [
    path("chargers", NearbyChargersView.as_view(), name="list-chargers"),
    path("chargers/<int:pk>/report", ReportChargerView.as_view(), name="charger-report"),
]
