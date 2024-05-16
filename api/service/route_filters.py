from django.db.models import Q
from django_filters import FilterSet
from common.models.route import Route
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta

from django_filters import CharFilter


class BaseRouteFilter(FilterSet):
    # Manually added fields to customize aspect and schema generation
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
    destination = CharFilter(
        field_name="destinationAlias",
        lookup_expr="icontains",
        label="Destination alias",
    )
    origin = CharFilter(
        field_name="originAlias", lookup_expr="icontains", label="Origin alias"
    )
    date = CharFilter(method="dateFilter",
                      label="Date of the route (YYYY-MM-DD)")

    def dateFilter(self, queryset, name, value):
        try:
            # Convert the provided date string to a datetime object
            date = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            # Handle invalid date format gracefully
            return queryset.none()

        # Calculate the start and end of the day for the provided date
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)

        # Filter the queryset by the date range
        return queryset.filter(departureTime__range=(start_of_day, end_of_day))

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


class BasePaginator(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100
