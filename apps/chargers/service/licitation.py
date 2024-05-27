import requests
from apps.chargers.interface.licitation import (
    LicitationService,
    Licitation,
)


class LicitAppService(LicitationService):
    """
    Service class for interacting with the LicitApp API.

    Attributes:
        LICITAPP_URL (str): The base URL of the LicitApp API.
        CREATE_ENDPOINT (str): The endpoint for creating a new licitation.
        CONTENT_TYPE (str): The content type for the request headers.

    Methods:
        createLicitation: Creates a new licitation by sending a POST request to the LICITAPP_URL.
    """

    LICITAPP_URL = "https://licitapp-back-f4zi3ert5q-oa.a.run.app"
    CREATE_ENDPOINT = "/licitacions/licitacio"
    CONTENT_TYPE = "application/json"

    def createLicitation(self, licitation: Licitation) -> None:
        """
        Creates a new licitation by sending a POST request to the LICITAPP_URL.

        Args:
            licitation (Licitation): The licitation object to be created.

        Raises:
            requests.HTTPError: If the POST request fails.

        Returns:
            None
        """
        r = requests.post(
            self.LICITAPP_URL,
            json=licitation.as_dict(),
            headers={"Content-Type": self.CONTENT_TYPE},
        )
        r.raise_for_status()
