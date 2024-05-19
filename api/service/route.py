import heapq
import json
from typing import Union

import numpy as np
import polyline
import requests
from api import GoogleMapsRouteClient
from api.serializers import CreateRouteSerializer, PreviewRouteSerializer
from common.models.charger import ChargerLocationType, LocationCharger
from common.models.route import Route
from common.models.user import Driver, User

# Dont remove, it is use for migrate well
from django.utils import timezone
from geopy.distance import distance
from google.maps.routing_v2 import ComputeRoutesRequest, ComputeRoutesResponse
from google.maps.routing_v2 import Route as GRoute
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from sklearn.neighbors import NearestNeighbors

X_GOOGLE_FIELDS = (
    "x-goog-fieldmask",
    "routes.distanceMeters,routes.duration,routes.polyline.encodedPolyline",
)


def buildMapsRouteRequest(
    serializer: Union[PreviewRouteSerializer, CreateRouteSerializer]
) -> ComputeRoutesRequest:
    """
    Creates a ComputeRoutesRequest object based on the passed data.

    Returns:
        ComputeRoutesRequest: The created ComputeRoutesRequest object.
    """
    mapping = {
        "origin": {
            "location": {
                "lat_lng": {
                    "latitude": serializer.validated_data.get("originLat"),  # type: ignore
                    "longitude": serializer.validated_data.get("originLon"),  # type: ignore
                }
            }
        },
        "destination": {
            "location": {
                "lat_lng": {
                    "latitude": serializer.validated_data.get("destinationLat"),  # type: ignore
                    "longitude": serializer.validated_data.get("destinationLon"),  # type: ignore
                }
            }
        },
    }
    computeRoutesRequest = ComputeRoutesRequest(mapping)
    return computeRoutesRequest


def deserializeMapsRoutesResponse(mapsRoute: ComputeRoutesResponse):
    """
    Derializes a ComputeRoutesResponse object into the serializer.

    Args:
        response (ComputeRoutesResponse): The ComputeRoutesResponse object to serialize.
    """
    assert isinstance(mapsRoute, ComputeRoutesResponse), "Wrong type for response parameter"

    if not mapsRoute.routes:
        raise ValueError("No routes found")

    route: GRoute = mapsRoute.routes[0]
    return {
        "polyline": route.polyline.encoded_polyline,
        "duration": route.duration.seconds,
        "distance": route.distance_meters,
    }


def computeMapsRoute(serializer: Union[PreviewRouteSerializer, CreateRouteSerializer]):
    """
    Computes the route using the Google Maps API based on the provided serializer.

    Args:
        serializer (Union[CreatePreviewRouteSerializer, CreateRouteSerializer]): The serializer object containing the route information.

    Returns:
        The deserialized response from the Google Maps API.
    """
    mapsPayload = buildMapsRouteRequest(serializer)

    # Initialize request argument(s)
    request = ComputeRoutesRequest(mapping=mapsPayload)
    response = GoogleMapsRouteClient.compute_routes(request=request, metadata=[X_GOOGLE_FIELDS])

    # Deserialize the response from the Google Maps API and send it back to the client
    return deserializeMapsRoutesResponse(response)


def buildMapsRouteRequestChargers(path: list):
    """
    Creates a payload for the Google Maps API.

    Args:
        path (list): The path from the Dijkstra's algorithm.
        origin (str): The origin.
        destination (str): The destination.
    """

    # Remove the origin and destination from the path
    waypoints = path[1:-1]

    # Format the waypoints into a string
    # waypoints_str = '|'.join(waypoints)
    intermediates = []
    for point in waypoints:
        intermediates.append(
            {
                "location": {
                    "lat_lng": {
                        "latitude": point[0],
                        "longitude": point[1],
                    }
                }
            }
        )

    mapping = {
        "origin": {
            "location": {
                "lat_lng": {
                    "latitude": float(path[0][0]),
                    "longitude": float(path[0][1]),
                }
            }
        },
        "destination": {
            "location": {
                "lat_lng": {
                    "latitude": float(path[-1][0]),
                    "longitude": float(path[-1][1]),
                }
            }
        },
        "intermediates": [],
    }
    mapping["intermediates"] = intermediates
    computeRoutesRequest = ComputeRoutesRequest(mapping)
    return computeRoutesRequest


def computeOptimizedRoute(
    serializer: Union[PreviewRouteSerializer, CreateRouteSerializer], driverId: int
):
    """
    Creates a ComputeOptimizedRoutesRequest object based on the passed data.

    Returns:
        ComputeOptimizedRoutesRequest: The created ComputeOptimizedRoutesRequest object.
    """
    # Refactor to outside method
    mapsPayload = buildMapsRouteRequest(serializer)
    request = ComputeRoutesRequest(mapping=mapsPayload)
    response = GoogleMapsRouteClient.compute_routes(request=request, metadata=[X_GOOGLE_FIELDS])

    # Decode the polyline
    decodedPolyline = polyline.decode(response.routes[0].polyline.encoded_polyline)

    # Get route bounds
    bounds = getRouteBounds(decodedPolyline)
    user = Driver.objects.get(id=driverId)
    # Convert ManyToManyRelatedManager to list
    driverChargerTypes = list(user.chargerTypes.all())
    chargersInArea = calculateChargerPoints(bounds, driverChargerTypes)
    # print(chargersInArea)

    # Create list with possible route points
    # [0] is origin, [-1] is destination
    routePoints = {"origin": decodedPolyline[0]}
    for charger in chargersInArea:
        routePoints[f"{charger['id']}"] = (charger["latitud"], charger["longitud"])
    routePoints["destination"] = decodedPolyline[-1]
    # print(routePoints)

    autonomy = user.autonomy  # type: ignore
    possibleRoutes = calculatePossibleRoute(routePoints, autonomy)
    # if len(possibleRoutes) == 1:
    #     possibleRoutes.append(decodedPolyline[0])
    mapsPayload = buildMapsRouteRequestChargers(possibleRoutes)
    print(mapsPayload)
    request = ComputeRoutesRequest(mapping=mapsPayload)
    response = GoogleMapsRouteClient.compute_routes(request=request, metadata=[X_GOOGLE_FIELDS])
    return {
        "route_data": deserializeMapsRoutesResponse(response),
        "charger_points": possibleRoutes[1:-2],
    }


def getRouteBounds(decodedPolyline: list):
    """
    Returns the area of the route.

    Args:
        decodedPolyline (list): The decoded polyline.
    """

    minLat = decodedPolyline[0][0]
    maxLat = decodedPolyline[0][0]
    minLong = decodedPolyline[0][1]
    maxLong = decodedPolyline[0][1]

    for coord in decodedPolyline:
        if coord[0] > maxLat:
            maxLat = coord[0]
        if coord[0] < minLat:
            minLat = coord[0]
        if coord[1] > maxLong:
            maxLong = coord[1]
        if coord[1] < minLong:
            minLong = coord[1]

    # Shouthwest: lower left corner, Northeast: upper right corner
    bounds = {"southwest": [minLat, minLong], "northeast": [maxLat, maxLong]}

    return bounds


def calculateChargerPoints(bounds: dict, chargerTypes: list):
    """
    Returns the charger points within the area of the route.

    Args:
        bounds (dict): The bounds of the route.
    """
    try:
        chargerTypeObjs = ChargerLocationType.objects.filter(chargerType__in=chargerTypes)
    except ChargerLocationType.DoesNotExist:
        raise ValidationError("Charger type does not exist", 400)
    print(chargerTypeObjs)
    # Get the charger points
    try:
        chargerPoints = LocationCharger.objects.filter(
            connectionType__in=chargerTypeObjs,
            acDc="AC",
            latitud__gte=bounds["southwest"][0],
            latitud__lte=bounds["northeast"][0],
            longitud__gte=bounds["southwest"][1],
            longitud__lte=bounds["northeast"][1],
        )
    except LocationCharger.DoesNotExist:
        raise ValidationError("Charger points do not exist", 400)
    print(len(chargerPoints))
    return list(chargerPoints.values())


def calculatePossibleRoute(routePoints: dict, autonomy: float):
    """
    Returns the possible routes based on the charger points.

    Args:
        routePoints (dict): The route points.
    """
    origin_to_destination_distance = distance(routePoints["origin"], routePoints["destination"]).km

    # If the distance is less than the autonomy, return a direct route
    if origin_to_destination_distance <= autonomy:
        return [routePoints["origin"], routePoints["destination"]]

    # Convert the route points to a numpy array
    routePointsArray = np.array(list(routePoints.values()))

    # Use the NearestNeighbors class from sklearn to find the k nearest neighbors
    # Adjust the number of neighbors as needed
    n_neighbors = min(100, len(routePointsArray) - 1)
    knn = NearestNeighbors(n_neighbors=n_neighbors)
    knn.fit(routePointsArray)

    routeGraph = {}
    # Create a list of keys from routePoints
    routePointsList = list(routePoints.keys())

    for i, originPoint in enumerate(routePointsList):
        routeGraph[originPoint] = {}

        # Get the indices of the k nearest neighbors
        neighbors = knn.kneighbors([routePointsArray[i]], return_distance=False)

        for neighbor in neighbors[0]:
            if neighbor != i:
                # Calculate the cost to go from originPoint to the neighbor
                cost = distance(routePoints[originPoint], routePoints[routePointsList[neighbor]]).km
                routeGraph[originPoint][routePointsList[neighbor]] = cost

    # print("routeGraph", routeGraph)
    # print("dijkstra", dijkstra(routeGraph, "origin", "destination"))
    order = dijkstra(routeGraph, "origin", "destination", autonomy)
    routeLangLong = []
    for point in order:
        routeLangLong.append(routePoints[point])
    return routeLangLong


def dijkstra(graph: dict, start: str, end: str, autonomy: float = 2.5):
    """
    Returns the shortest path and distance from the start to the end node in the graph.

    Args:
        graph (dict): The graph.
        start (str): The start node.
        end (str): The end node.
        autonomy (float): The autonomy in kilometers.
    """

    # Initialize the distance to every node as infinity, except the start node
    distances = {node: float("infinity") for node in graph}
    distances[start] = 0

    # Initialize the priority queue with the start node
    queue = [(0, start)]

    # Initialize the parent dictionary
    parents = {node: None for node in graph}

    while queue:
        # Get the node with the smallest distance
        current_distance, current_node = heapq.heappop(queue)

        # If the current distance is larger than the stored distance, skip this node
        if current_distance > distances[current_node]:
            continue

        # If the current node is the end node, break the loop
        if current_node == end:
            break

        # Update the distances to the neighboring nodes
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor] and weight <= autonomy:
                distances[neighbor] = distance
                parents[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))

    # Build the path from start to end
    path = []
    current_node = end
    while current_node is not None:
        path.append(current_node)
        current_node = parents[current_node]
    path.reverse()

    return path


def validateJoinRoute(routeId: int, passengerId: int):
    """
    Validates if a user can join a route.

    Args:
        route_id (int): The ID of the route.
        user_id (int): The ID of the user.
    """
    route = Route.objects.get(id=routeId)
    if route.driver.pk == passengerId:
        raise ValidationError("Driver can't join the route", 400)

    if route.isFull():
        raise ValidationError("Route is full", 400)

    if route.passengers.filter(id=passengerId).exists():
        raise ValidationError("User is already in the route", 400)

    if route.cancelled:
        raise ValidationError("You can not join a cancelled route", 400)

    if route.finalized:
        raise ValidationError("You can not join a finalized route", 400)

    # check if the user is already in a route that overlaps with the current route
    joinedRoutes = route.passengers.filter(id=passengerId)
    for joinedRoute in joinedRoutes:
        if route.overlapsWith(joinedRoute.route):
            raise ValidationError(
                "User is already in a route that overlaps with the current route", 400
            )


def joinRoute(routeId: int, passengerId: int, paymentMethodId: str):
    """
    Joins a user to a route after payment is successfull.

    Args:
        route_id (int): The ID of the route.
        user_id (int): The ID of the user.
    """
    try:
        route = Route.objects.get(id=routeId)
    except Route.DoesNotExist:
        raise ValidationError("Route does not exist", 400)

    try:
        token = Token.objects.get(user_id=passengerId)
    except Token.DoesNotExist:
        raise ValidationError("User does not have a token", 400)

    url = "http://payments-api:8000/process_payment/"
    data = {
        "payment_method_id": paymentMethodId,
        "route_id": routeId,
    }
    headers = {"Content-Type": "application/json", "Authorization": "Token " + token.key}
    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code != 200:
        raise ValidationError("Payment failed and user did not join the route", 400)

    passenger = User.objects.get(id=passengerId)
    route.passengers.add(passenger)


def leaveRoute(routeId: int, passengerId: int):
    """
    Leaves a user from a route.

    Args:
        route_id (int): The ID of the route.
        user_id (int): The ID of the user.
    """
    route = Route.objects.get(id=routeId)
    if not route.passengers.filter(id=passengerId).exists():
        raise ValidationError("User is not in the route", 400)

    # Only refund if more than 24 hours before the departure time
    if (route.departureTime - timezone.now()).days >= 1:
        try:
            token = Token.objects.get(user_id=passengerId)
        except Token.DoesNotExist:
            raise ValidationError("User does not have a token", 400)

        url = "http://payments-api:8000/refund/"
        data = {
            "route_id": routeId,
        }
        headers = {"Content-Type": "application/json", "Authorization": "Token " + token.key}
        response = requests.post(url, data=json.dumps(data), headers=headers)

        if response.status_code != 200:
            raise ValidationError("Refund failed and User did not leave the route", 400)

    route.passengers.remove(User.objects.get(id=passengerId))


def forcedLeaveRoute(routeId: int, passengerId: int):
    """
    Forces a user to leave a route.

    Args:
        route_id (int): The ID of the route.
        user_id (int): The ID of the user.
    """
    route = Route.objects.get(id=routeId)
    if not route.passengers.filter(id=passengerId).exists():
        raise ValidationError("User is not in the route", 400)

    try:
        token = Token.objects.get(user_id=passengerId)
    except Token.DoesNotExist:
        raise ValidationError("User does not have a token", 400)

    url = "http://payments-api:8000/refund/"
    data = {
        "route_id": routeId,
    }
    headers = {"Content-Type": "application/json", "Authorization": "Token " + token.key}
    requests.post(url, data=json.dumps(data), headers=headers)

    # If refund fails, user is still removed from the route.
    # Contact us by email to resolve the issue.
    route.passengers.remove(User.objects.get(id=passengerId))
