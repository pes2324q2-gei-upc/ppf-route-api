import os
from google.api_core.client_options import ClientOptions
from google.maps.routing_v2 import RoutesClient

CLIENT_OPTIONS = {"api_key": os.environ.get("BACKEND_MAPS_API"), "quota_project_id": os.environ.get("PROJECT_ID")}
GoogleMapsRouteClient = RoutesClient(
    client_options=CLIENT_OPTIONS,
)
