from abc import ABC, abstractmethod


class AbstractLicitationService(ABC):
    @abstractmethod
    def createLicitation(self, data):
        # Implementation goes here
        pass
