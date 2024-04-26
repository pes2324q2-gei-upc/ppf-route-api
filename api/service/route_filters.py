from curses import meta
from django_filters import FilterSet
from common.models.route import Route
from drf_yasg.inspectors import NotHandled


class BaseRouteFilter(FilterSet):
    class Meta:
        model = Route
        fields = {
            "originLat": ["exact"],
            "originLon": ["exact"],
            "destinationLat": ["exact"],
            "destinationLon": ["exact"],
            "driver": ["exact"],
            "passengers": ["contains"],
            "freeSeats": ["gte"],
        }
