from django.db.models import Q
from django_filters import FilterSet
from common.models.route import Route

from django_filters import CharFilter


class BaseRouteFilter(FilterSet):
    user = CharFilter(method="userFilter")

    def userFilter(self, queryset, name, value):
        return queryset.filter(Q(driver__id=value) | Q(passengers__id__in=value))

    class Meta:
        model = Route
        fields = {
            "originLat": ["exact"],
            "originLon": ["exact"],
            "destinationLat": ["exact"],
            "destinationLon": ["exact"],
            "driver__id": ["exact"],
            "passengers__id": ["in"],
            "freeSeats": ["gte"],
        }
