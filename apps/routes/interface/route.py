from abc import ABC, abstractmethod
from typing import Dict
from geopy.distance import distance


class LatLon:
    def __init__(self, lat: float, lon: float):
        self.latitude = lat
        self.longitude = lon

    def __eq__(self, other):
        return self.latitude == other.latitude and self.longitude == other.longitude

    def __hash__(self):
        return hash((self.latitude, self.longitude))

    def dist(self, other: "LatLon") -> float:
        return distance((self.latitude, self.longitude), (other.latitude, other.longitude)).meters

    def distKm(self, other: "LatLon") -> float:
        return self.dist(other) / 1000


class ComputeRouteService(ABC):
    @abstractmethod
    def computeRoute(self, origin: LatLon, destination: LatLon) -> dict:
        pass

    @abstractmethod
    def computeChargingRoute(self, origin: LatLon, destination: LatLon, autonomy: float) -> dict:
        pass


class RouteService(ABC):
    @abstractmethod
    def createRoute(self, route: dict):
        pass

    @abstractmethod
    def canJoinRoute(self, route: str, user: str) -> bool:
        pass

    @abstractmethod
    def joinRoute(self, route: str, user: str):
        pass

    @abstractmethod
    def leaveRoute(self, route: str, user: str):
        pass

    @abstractmethod
    def forcedLeaveRoute(self, route: str, user: str):
        pass

    @abstractmethod
    def finalizeRoute(self, route: str):
        pass

    @abstractmethod
    def cancelRoute(self, route: str):
        pass
