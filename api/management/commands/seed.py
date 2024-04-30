import requests
from django.core.management.base import BaseCommand
from common.models.charger import LocationCharger, ChargerVelocity, ChargerLocationType


class Command(BaseCommand):
    help = 'Populates the database with charger data from the API'

    def handle(self, *args, **options):
        response = requests.get(
            'https://analisi.transparenciacatalunya.cat/resource/tb2m-m33b.json')
        data = response.json()

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
            connection_types = item['tipus_connexi'].split('+')
            for connection_type in connection_types:
                if connection_type == "MENNEKES.M":
                    connection_type = "MENNEKES"
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
