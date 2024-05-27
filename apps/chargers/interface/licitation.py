from abc import ABC, abstractmethod

from common.models.charger import LocationCharger


class Licitation:
    def __init__(self, charger: LocationCharger):
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


class LicitationService(ABC):
    """
    Abstract base class for licitation services.
    """

    @abstractmethod
    def createLicitation(self, licitation: Licitation) -> None:
        pass
