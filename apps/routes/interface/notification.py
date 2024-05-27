from abc import ABC, abstractmethod
from enum import Enum


class Notification:
    """
    Represents a notification with a title and body.
    The class provides static methods to create different types of notifications.
    """

    class Priority(Enum):
        HIGH = "high"
        NORMAL = "normal"

    def __init__(self, title: str, body: str, priority: Priority = Priority.NORMAL):
        self.title = title
        self.body = body
        self.priority = priority

    @staticmethod
    def routeStarted(destination: str):
        title = "Route Started"
        body = f"The route to {destination} has started"
        return Notification(title, body, Notification.Priority.HIGH)

    @staticmethod
    def routeEnded(destination: str):
        title = "Route Ended"
        body = f"The route to {destination} has ended"
        return Notification(title, body)

    @staticmethod
    def routeCancelled(destination: str):
        title = "Route Canceled"
        body = f"The route to {destination} has been canceled"
        return Notification(title, body, Notification.Priority.HIGH)

    @staticmethod
    def passengerJoined(destination: str):
        title = "Passenger Joined"
        body = f"A passenger has joined your route to {destination}"
        return Notification(title, body)

    @staticmethod
    def passengerLeft(destination: str):
        title = "Passenger Left"
        body = f"A passenger has left your route to {destination}"
        return Notification(title, body)


class NotificationService(ABC):
    """
    Abstract base class for notification services.
    """

    @abstractmethod
    def notify(self, user: str, title: str, body: str, priority: str):
        """
        Sends a notification to a user.

        Args:
            user (str): The user to send the notification to.
            title (str): The title of the notification.
            body (str): The body of the notification.
            priority (str): The priority of the notification.

        Returns:
            None
        """
        pass

    @abstractmethod
    def notifyPassengers(self, route: str, notification: Notification):
        """
        Sends a notification to all passengers of a route.

        Args:
            route (str): The route identifier.
            notification (str): The notification message.

        Returns:
            None
        """
        pass

    @abstractmethod
    def notifyDriver(self, route: str, notification: Notification):
        """
        Sends a notification to the driver of a route.

        Args:
            route (str): The route identifier.
            notification (str): The notification message.

        Returns:
            None
        """
        pass
