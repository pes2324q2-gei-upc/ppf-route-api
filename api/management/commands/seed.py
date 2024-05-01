import requests
from django.core.management.base import BaseCommand
from common.models.charger import LocationCharger, ChargerVelocity, ChargerLocationType
import re


class Command(BaseCommand):
    help = 'Populates the database with charger data from the API'

    def handle(self, *args, **options):
        response = requests.get(
            'https://analisi.transparenciacatalunya.cat/resource/tb2m-m33b.json?$limit=2000')
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
                    print(connection_type)
                    charger_type = ChargerLocationType.objects.get_or_create(
                        chargerType=connection_type
                    )
                    charger.connectionType.add(charger_type[0])

            # Add velocities
            velocities = item['tipus_velocitat'].split(' i ')
            for velocity in velocities:
                try:
                    charger_velocity = ChargerVelocity.objects.get(
                        velocity=velocity.strip()
                    )
                    charger.velocities.add(charger_velocity)

                except ChargerVelocity.DoesNotExist:
                    print("THIS ONE DID NOT WORK", velocity)

    def clear_data(self):
        LocationCharger.objects.all().delete()
