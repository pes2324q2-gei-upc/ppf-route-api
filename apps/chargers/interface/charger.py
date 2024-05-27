from abc import ABC, abstractmethod

from common.models.charger import LocationCharger


class ChargerService(ABC):
    """
    Abstract base class for charger controllers.
    """

    @abstractmethod
    def getByLocation(self, lat: float, lon: float, radius: float) -> list[LocationCharger]:
        pass
