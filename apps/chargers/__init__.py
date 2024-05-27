from chargers.interface.licitation import Licitation, LicitationService
from chargers.service.licitation import LicitAppService, LicitationService
from chargers.service.charger import ChargerService, DjangoChargerService

licitationService: LicitationService = LicitAppService()
chargerController: ChargerService = DjangoChargerService()
