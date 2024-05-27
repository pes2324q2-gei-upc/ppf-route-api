import os
from google.maps.routing_v2 import RoutesClient
from apps.routes.interface.route import ComputeRouteService, RouteService
from apps.routes.interface.user import UserService
from apps.routes.service.route import DjangoRouteService, GMapsRouteService
from apps.routes.service.user import DjangoUserService

from apps.routes.interface.route import LatLon

CLIENT_OPTIONS = {
    "api_key": os.environ.get("BACKEND_MAPS_API", "none"),
    "quota_project_id": os.environ.get("PROJECT_ID", "none"),
}
GoogleMapsRouteClient = RoutesClient(client_options=CLIENT_OPTIONS)

computeRouteService: ComputeRouteService = GMapsRouteService(GoogleMapsRouteClient)
routesService: RouteService = DjangoRouteService()
userService: UserService = DjangoUserService()
