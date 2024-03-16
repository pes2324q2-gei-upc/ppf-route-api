import datetime
import json
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch

from ppf.common.models.route import Route
from ppf.common.models.user import Driver

from .payloads import CREATE_ROUTE_PAYLOAD, RETRIEVE_ROUTE_RESPONSE
from .payloads import CREATE_ROUTE_PREVIEW_RESPONSE
from .payloads import CREATE_ROUTE_RESPONSE
from .payloads import MAPS_COMPUTE_RESPONSE
from .payloads import CREATE_ROUTE_PREVIEW_PAYLOAD
from .polyline import POLYLINE


class RouteCreateTestCase(APITestCase):
    """
    Test case for the route list create view.
    """

    def testCreateRoute(self):
        """
        Test case for creating a route.
        """
        data = CREATE_ROUTE_PAYLOAD

        with patch("api.views.computeRoute") as mock_computeRoute:
            mock_computeRoute.return_value = MAPS_COMPUTE_RESPONSE
            response = self.client.post("/routes", data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data, CREATE_ROUTE_RESPONSE)

    def testCreateRoutePreview(self):
        """
        Test case for creating a preview route.
        """
        with patch("api.views.computeRoute") as mock_computeRoute:
            mock_computeRoute.return_value = MAPS_COMPUTE_RESPONSE
            response = self.client.post("/routes", CREATE_ROUTE_PREVIEW_PAYLOAD, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, CREATE_ROUTE_PREVIEW_RESPONSE)


class RouteRUDTestCase(APITestCase):
    """
    Test case for the route retrieve update destroy view.
    """

    def setUp(self) -> None:
        Route.objects.create(
            driver=1,
            originLat=41.389972,
            originLon=2.115333,
            originAlias="BSC - Supercomputing Center",
            destinationLat=42.244062,
            destinationLon=-6.269438,
            destinationAlias="Morla de la Valdería",
            polyline=POLYLINE,
            distance=852896,
            duration=30177,
            departureTime=datetime.datetime(2024, 10, 6, 10, 0, 0),
            freeSeats=4,
            price=63.50,
            cancelled=False,
            finalized=False,
            createdAt=datetime.datetime.now(),
        )
        return super().setUp()

    def testRetrieveRoute(self):
        """
        Test case for retrieving a route.
        """
        # Mock the route creation

        # Retrieve the route
        response = self.client.get(f"/routes/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, RETRIEVE_ROUTE_RESPONSE)

    def testUpdateRoute(self):
        """
        Test case for updating a route.
        """
        assert False, "Not implemented"

    def testDestroyRoute(self):
        """
        Test case for destroying a route.
        """
        response = self.client.delete("/routes/1")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def testCancelRoute(self):
        """
        Test case for canceling a route.
        """
        data = {"routeId": 1}
        response = self.client.post("/routes/1/cancel", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def testJoinRoute(self):
        """
        Test case for joining a route.
        """
        data = {"routeId": 1, "passenjerId": 1}
        response = self.client.post("/routes/1/join", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testLeaveRoute(self):
        """
        Test case for leaving a route.
        """
        data = {"routeId": 1, "passenjerId": 1}
        response = self.client.post("/routes/1/leave", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testFinishRoute(self):
        """
        Test case for finishing a route.
        """
        data = {"routeId": 1, "driverId": 1}
        response = self.client.post("/routes/1/finish", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


"""
TODO add test cases for edge cases and error handling
- Case when maps API cannot compute the route
- Case when route is not found
- Case finish when route is already finished
- Case join, leave and cancel when route is already finished
- Case join and leave when route is cancelled
- Case join when route is full
- Case leave when passenjer is not part of the route
- Case leave when passenjer is the driver
- Case finish when driver is not the driver of the route
"""
