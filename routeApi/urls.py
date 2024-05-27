from rest_framework import authentication, permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from api.v2.views import ListRoutes
from api.views import (
    FinishRoute,
    NearbyChargersView,
    RouteCancelView,
    LicitacioService,
    RoutePassengersList,
    RouteJoinView,
    RouteLeaveView,
    RouteListCreateView,
    RoutePassengersList,
    RoutePreviewView,
    RouteRetrieveView,
    RouteValidateJoinView,
)
from django.urls import path

urlpatterns = []

from apps.chargers.views import urls as chargers_urls
from apps.routes.views.v1 import urls as routes_v1_urls
from apps.routes.views.v2 import urls as routes_v2_urls

urlpatterns += chargers_urls
urlpatterns += routes_v1_urls
urlpatterns += routes_v2_urls

schema_view = get_schema_view(
    openapi.Info(
        title="Routes API",
        default_version="v1",
        description="The routes API provides a way to compute routes between two points.",
        terms_of_service="https://www.google.com/policies/terms/",
        license=openapi.License(name="Apache 2.0 License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[authentication.TokenAuthentication],
)

urlpatterns += [
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
]
