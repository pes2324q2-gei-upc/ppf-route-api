from enum import Enum
from requests import HTTPError, post

from common.models.route import Route

NOTIFY_API_URL = "http://user-api:8000/api/service/notify"


from enum import Enum


class Notification(Enum):
    """
    Enum class representing different types of notifications.
    Each notification has a title and a body.
    Body can be formatted with the destination of the route.
    """

    ROUTE_STARTED = ("Route Started", "The route to {destination} has started")
    ROUTE_ENDED = ("Route Ended", "The route to {destination} has ended")
    ROUTE_CANCELLED = ("Route Canceled", "The route to {destination} has been canceled")
    PASSENGER_JOINED = ("Passenger Joined", "A passenger has joined your route to {destination}")
    PASSENGER_LEFT = ("Passenger Left", "A passenger has left your route to {destination}")

    @property
    def title(self):
        """
        Get the title of the notification.
        """
        return self.value[0]

    @property
    def body(self):
        """
        Get the body of the notification.
        """
        return self.value[1]


def notify(user: str, title: str, body: str):
    """
    Sends a notification to a certain user.

    Args:
        user (str): The username of the recipient.
        title (str): The title of the notification.
        body (str): The body content of the notification.

    Raises:
        HTTPError: If the request to send the notification fails.

    """
    try:
        # Send a http request to user-api to send a notification to a certain user
        response = post(NOTIFY_API_URL, json={"user": user, "title": title, "body": body})
        response.raise_for_status()  # Raise an exception if the request was not successful
    except HTTPError as e:
        # Log the error message if the request fails
        assert False, f"Failed to send notification: {e}"


def notifyPassengers(routeId: str, ntf: Notification):
    """
    Notifies all passengers of a given route.

    Args:
        routeId (str): The ID of the route.
        ntf (Notification): The notification object containing the title and body.

    Returns:
        None
    """
    # get route passengers user id
    route: Route | None = Route.objects.get(id=routeId).first()
    if route is not None:
        passengers = route.passengers.all()
        # Notify all passengers that the route has started
        for passenger in passengers:
            notify(passenger.pk, ntf.title, ntf.body)


def notifyDriver(routeId: str, ntf: Notification):
    """
    Notifies the driver of a route about a passenger joining the route.

    Args:
        routeId (str): The ID of the route.
        ntf (Notification): The notification object containing the title and body.

    Returns:
        None
    """
    # get route driver user id
    route: Route | None = Route.objects.get(id=routeId).first()
    if route is not None:
        driver = route.driver.pk
        # Notify the driver that a passenger has joined the route
        notify(driver, ntf.title, ntf.body.format(destination=route.destinationAlias))
