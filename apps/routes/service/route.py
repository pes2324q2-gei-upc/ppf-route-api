from common.models.route import Route
from apps.routes.interface.route import LatLon, ComputeRouteService, RouteService


class GMapsRouteService(ComputeRouteService):
    """
    A route service implementation that uses Google Maps API to compute routes.
    """

    def __init__(self, client):
        self.mapsClient = client

    def computeRoute(self, origin: LatLon, destination: LatLon) -> dict:
        return {}

    def computeChargingRoute(self, origin: LatLon, destination: LatLon, autonomy: float) -> dict:
        return {}


class DjangoRouteService(RouteService):

    def createRoute(self, route: dict):
        pass

    def canJoinRoute(self, route: str, user: str) -> bool:
        return False

    def joinRoute(self, route: str, user: str):
        pass

    def leaveRoute(self, route: str, user: str):
        pass

    def forcedLeaveRoute(self, route: str, user: str):
        pass

    def finalizeRoute(self, route: str):
        pass

    def cancelRoute(self, route: str):
        pass
