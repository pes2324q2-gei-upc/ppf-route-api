import requests
from abc import ABC, abstractmethod


class Licitation:
    def __init__(self, charger):
        self.latitud = charger.latitud
        self.longitud = charger.longitud
        self.nom_organ = charger.promotorGestor
        self.tipus = "Servei"
        self.procediment = "Obert"
        self.fase_publicacio = "Formalització"
        self.denominacio = "Servei de recàrrega de vehicles elèctrics"
        self.lloc_execucio = charger.adreA
        self.nom_ambit = "PowerPathFinder"
        self.pressupost = 3.69

    def as_dict(self):
        return {
            "latitud": self.latitud,
            "longitud": self.longitud,
            "nom_organ": self.nom_organ,
            "tipus": self.tipus,
            "procediment": self.procediment,
            "fase_publicacio": self.fase_publicacio,
            "denominacio": self.denominacio,
            "lloc_execucio": self.lloc_execucio,
            "nom_ambit": self.nom_ambit,
            "pressupost": self.pressupost,
        }


class AbstractLicitationService(ABC):
    """
    Abstract base class for licitation services.
    """

    @abstractmethod
    def createLicitation(self, data):
        pass


class LicitAppService(AbstractLicitationService):
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

    def createLicitation(self, licitation: Licitation):
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
