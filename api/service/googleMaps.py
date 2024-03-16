import logging
from google.maps.routing_v2 import RoutesClient, ComputeRoutesRequest, ComputeRoutesResponse


def computeRoute(routePayload: dict, client: RoutesClient) -> ComputeRoutesResponse:
    # Initialize request argument(s)
    request = ComputeRoutesRequest(mapping=routePayload)
    response = client.compute_routes(request=request)
    # Handle the response
    logging.info(response)
    return response
