import logging

from apps.routes.interface.notification import Notification, NotificationService
from common.models.route import Route
from requests import HTTPError, post


class FirebaseNotificationService(NotificationService):
    NOTIFY_API_URL = "http://user-api:8000/push/notify"
    routeManager = Route.objects

    def notify(self, user: str, title: str, body: str, priority: str):
        try:
            # Send a http request to user-api to send a notification to a certain user
            response = post(
                self.NOTIFY_API_URL + f"/{user}",
                json={"user": user, "title": title, "body": body, "priority": priority},
            )
            response.raise_for_status()  # Raise an exception if the request was not successful
        except HTTPError as e:
            # Log the error message if the request fails
            logging.error(e.strerror)
            pass

    def notifyPassengers(self, route: str, ntf: Notification):
        r: Route | None = self.routeManager.get(id=route)
        if r is not None:
            passengers = r.passengers.all()
            # Notify all passengers
            for passenger in passengers:
                self.notify(passenger.pk, ntf.title, ntf.body, ntf.priority.value)
        else:
            logging.error(f"Route with id {route} not found")

    def notifyDriver(self, route: str, ntf: Notification):
        """
        Notifies the driver of a route about a passenger joining the route.

        Args:
            routeId (str): The ID of the route.
            ntf (Notification): The notification object containing the title and body.

        Returns:
            None
        """
        # get route driver user id
        r: Route | None = self.routeManager.get(id=route)
        if r is not None:
            driver = r.driver.pk
            # Notify the driver that a passenger has joined the route
            self.notify(driver, ntf.title, ntf.body, ntf.priority.value)
        else:
            logging.error(f"Route with id {route} not found")
