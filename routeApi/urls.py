from django.urls import path
from api.views import RouteRetrieveView, RoutePreviewView, RouteListCreateView

urlpatterns = [
    path("routes", RouteListCreateView.as_view(), name="route-list-create"),
    path("routes/preview", RoutePreviewView.as_view(), name="route-list-create"),
    path("routes/<int:pk>", RouteRetrieveView.as_view(), name="route-detail"),
]

from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

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
)

urlpatterns = urlpatterns + [
    path("swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
