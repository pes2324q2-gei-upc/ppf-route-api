from math import atan2, cos, radians, sin, sqrt
from typing import List

from apps.chargers.interface.charger import ChargerService
from common.models.charger import LocationCharger

EARTH_RATIO = 6371


class DjangoChargerService(ChargerService):
    """
    Service class for managing chargers.
    """

    manager = LocationCharger.objects

    def getByLocation(self, lat: float, lon: float, radius: float) -> list[LocationCharger]:
        """
        Retrieves a list of chargers within a specified radius of a given location.

        Args:
            lat (float): The latitude of the location.
            lon (float): The longitude of the location.
            radius (float): The radius in kilometers.

        Returns:
            list[LocationCharger]: A list of chargers within the specified radius.
        """
        cargadores_cercanos = []

        for cargador in self.manager.all():
            # Apply the haversine formula to calculate the distance between two points
            lat1, lon1, lat2, lon2 = map(radians, [lat, lon, cargador.latitud, cargador.longitud])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distancia = EARTH_RATIO * c  # Radio of the Earth in km

            # If the charger is within the radius, add it to the list
            if distancia <= radius:
                cargadores_cercanos.append(cargador)
        return cargadores_cercanos
