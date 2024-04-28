from django.db.models import Q
from django_filters import FilterSet
from common.models.route import Route

from django_filters import CharFilter


class BaseRouteFilter(FilterSet):
    user = CharFilter(
        method="userFilter",
        label="A user id that belongs to the route, both as passenger or driver",
    )
    driver = CharFilter(field_name="driver_id")
    passengers = CharFilter(
        field_name="passengers_id",
        lookup_expr="in",
        label="List of user Ids that 'could' be passengers of a route",
    )
    seats = CharFilter(
        field_name="freeSeats", lookup_expr="gte", label="Minimum number of free seats"
    )

    def userFilter(self, queryset, name, value):
        return queryset.filter(Q(driver__id=value) | Q(passengers__id__in=value))

    class Meta:
        model = Route
        fields = {
            "originLat": ["exact"],
            "originLon": ["exact"],
            "destinationLat": ["exact"],
            "destinationLon": ["exact"],
        }