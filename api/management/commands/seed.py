import requests
from django.core.management.base import BaseCommand
from common.models.charger import LocationCharger, ChargerVelocity, ChargerLocationType
import logging
import os


class Command(BaseCommand):
    help = 'Populates the database with charger data from the API'
    path = "api/logs"
    if not os.path.exists(path):
        os.makedirs(path)

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        self.stdout.write(self.style.NOTICE(
            "Populating database with charger data..."))

        try:
            response = requests.get(
                'https://analisi.transparenciacatalunya.cat/resource/tb2m-m33b.json?$limit=50000')
        except Exception as error:
            logging.basicConfig(filename='api/logs/db_logs.log',
                                encoding='utf-8', level=logging.ERROR)
            logger.error(error)
            self.stdout.write(self.style.ERROR(
                "Error while trying to fetch data from the API"))
            return

        data = response.json()

        accepted_types = ['MENNEKES', 'SCHUKO',
                          'TESLA', 'CHADEMO', 'CCS COMBO2']

        for item in data:

            # Create LocationCharger object
            charger = LocationCharger(
                promotorGestor=item['promotor_gestor'],
                access=item['acces'],
                kw=item['kw'],
                acDc=item['ac_dc'],
                latitud=item['latitud'],
                longitud=item['longitud'],
                adreA=item['adre_a']
            )
            charger.save()

            # Add connection types
            connection_types = item['tipus_connexi'].upper()
            for accepted_type in accepted_types:
                if accepted_type in connection_types:
                    connection_type = accepted_type
                    try:
                        charger_type = ChargerLocationType.objects.get(
                            chargerType=connection_type
                        )
                        charger.connectionType.add(charger_type)

                    except Exception as error:
                        logging.basicConfig(filename='api/logs/db_logs.log',
                                            encoding='utf-8', level=logging.WARNING)
                        logger.warning(error)
                        self.stdout.write(self.style.WARNING(
                            "Error while trying to add connection type: " + connection_type))

            # Add velocities
            velocities = item['tipus_velocitat'].split(' i ')
            for velocity in velocities:
                try:
                    charger_velocity = ChargerVelocity.objects.get(
                        velocity=velocity.strip()
                    )
                    charger.velocities.add(charger_velocity)

                except Exception as error:
                    logging.basicConfig(filename='api/logs/db_logs.log',
                                        encoding='utf-8', level=logging.WARNING)
                    logger.warning(error)
                    self.stdout.write(self.style.WARNING(
                        "Error while trying to add velocity: " + velocity))

        self.stdout.write(self.style.SUCCESS('Data seeded successfully'))

    def clear_data(self):
        try:
            LocationCharger.objects.all().delete()
        except:
            logger = logging.getLogger(__name__)
            logging.basicConfig(filename='api/logs/db_logs.log',
                                encoding='utf-8', level=logging.ERROR)
            logger.error('Error while trying to delete data from the database')
            return
