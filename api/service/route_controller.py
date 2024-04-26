from abc import ABC, abstractmethod
from django.http import QueryDict
from django_filters import FilterSet
from common.models.route import Route, RouteManager


class AbstractRouteController(ABC):
    """
    Defines the interface to be followed by any concrete implementation
    A RouteManager defines the domain operations of the RouteAPI
    """

    @abstractmethod
    def createRoute(serializer) -> Route:
        pass

    @abstractmethod
    def storeRoute(route):
        pass

    @abstractmethod
    def startRoute(routeId) -> bool:
        pass

    @abstractmethod
    def stopRoute(routeId) -> bool:
        pass

    @abstractmethod
    def cancelRoute(routeId) -> bool:
        pass

    @abstractmethod
    def joinPassenger(routeId, passengerId) -> bool:
        pass

    @abstractmethod
    def leavePassenger(routeId, passengerId) -> bool:
        pass

    @abstractmethod
    def findRouteByQuery(self, queryData: QueryDict):
        pass


class BaseRouteFilter(FilterSet):
    class Meta:
        model = Route
        fields = {
            "originLat": ["exact"],
            "originLon": ["exact"],
            "destinationLat": ["exact"],
            "destinationLon": ["exact"],
            "driver": ["exact"],
            "passenger": ["contains"],
            "freeSeats": ["gte"],
        }


class RouteFilter(BaseRouteFilter):
    pass


class RouteController(AbstractRouteController):
    routeManager: RouteManager = Route.objects
    find_filter = BaseRouteFilter

    # TODO determine if accepting the serializer is the best approach
    def createRoute(self, serializer) -> Route:
        raise NotImplementedError()

    def storeRoute(self, route) -> bool:
        raise NotImplementedError()

    def startRoute(self, routeId) -> bool:
        raise NotImplementedError()

    def stopRoute(self, routeId) -> bool:
        raise NotImplementedError()

    def cancelRoute(self, routeId) -> bool:
        raise NotImplementedError()

    def joinPassenger(self, routeId, passengerId) -> bool:
        raise NotImplementedError()

    def leavePassenger(self, routeId, passengerId) -> bool:
        raise NotImplementedError()

    def findRouteByQuery(self, queryData: QueryDict):
        filter = RouteFilter(data=queryData, queryset=self.routeManager.free())
        return filter.qs.get()
