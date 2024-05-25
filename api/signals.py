"""
This module contains the signals to update the achievements of the users
These signals are created in this repository because the ppf-user-api ca not catch the signals of the ppf-route-api
"""

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from common.models.achievement import UserAchievementProgress, Achievement
from common.models.route import Route
from common.models.user import User
from .service.calendar import add_event_calendar
import datetime


# Create 1, 10 and 50 routes
@receiver(post_save, sender=Route)
def route_created(sender, instance, created, **kwargs):
    if created:
        achievements = Achievement.objects.filter(
            title__in=["PrimeraVez", "ArquitectoViajero", "MaestroDeRutas"]
        )

        for achievement in achievements:
            user_achievement, _ = UserAchievementProgress.objects.get_or_create(
                user=instance.driver, achievement=achievement
            )

            check_and_increment_progress(user_achievement, achievement, instance)


# Join 1, 10 and 50 routes
@receiver(m2m_changed, sender=Route.passengers.through)
def route_joined(sender, instance, action, pk_set, **kwargs):
    # pk_set contains the ids of the users that have been added or removed to the M2M relation
    if action == "post_add":
        achievements = Achievement.objects.filter(
            title__in=["InfiltRuta", "ExploradorDecenal", "NomadaIntrepido"]
        )

        for user_id in pk_set:
            try:
                user = User.objects.get(pk=user_id)
                for achievement in achievements:
                    user_achievement, _ = UserAchievementProgress.objects.get_or_create(
                        user=user, achievement=achievement
                    )

                    check_and_increment_progress(user_achievement, achievement, instance)
            except User.DoesNotExist:
                pass


# End 1 route
@receiver(post_save, sender=Route)
def route_finalized(sender, instance, created, **kwargs):
    if not (created) and instance.finalized:
        try:
            achievement = Achievement.objects.get(title="FinalFeliz")
        except Achievement.DoesNotExist:
            return

        user_achievement, _ = UserAchievementProgress.objects.get_or_create(
            user=instance.driver, achievement=achievement
        )

        check_and_increment_progress(user_achievement, achievement, instance)


def check_and_increment_progress(user_achievement, achievement, instance):
    if not user_achievement.achieved:
        user_achievement.progress += 1
        if user_achievement.progress >= achievement.required_points:
            user_achievement.achieved = True
            user_achievement.date_achieved = instance.createdAt
        user_achievement.save()


# Create a calendar event to the driver when a route is created
@receiver(post_save, sender=Route)
def route_created_calendar_event(sender, instance, created, **kwargs):
    if created:

        if isinstance(instance.duration, int):
            instance.duration = datetime.timedelta(seconds=instance.duration)

        event_data = {
            "summary": f"Route {instance.id}",
            "location": f"{instance.originAlias} - {instance.destinationAlias}",
            "description": f"Route from {instance.originAlias} to {instance.destinationAlias}",
            "start": {
                "dateTime": instance.departureTime.isoformat(),
                "timeZone": "Europe/Madrid",
            },
            "end": {
                "dateTime": (instance.departureTime + instance.duration).isoformat(),
                "timeZone": "Europe/Madrid",
            },
            "reminders": {
                "useDefault": True,
            },
        }

        # Try to add the event to the driver's calendar
        try:
            add_event_calendar(instance.driver, instance, event_data)
        except Exception:
            pass