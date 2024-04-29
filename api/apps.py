from django.apps import AppConfig
from django.core.management import call_command


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

   # def ready(self):
   #    call_command("seed")    # Seed the database
   #    return super().ready()
