import logging
from django.db.models import F
from ppf.common.models.route import Route, RoutePassenjer


def cancelRoute(routeId: int):
    Route.objects.filter(id=routeId).update(cancelled=True)
    logging.info(f"Route {routeId} was cancelled")


async def notifyRouteCancelled(routeId: int):
    logging.warning("notifyRouteCancelled function is not yet implemented")


async def refundPassenjersFee(routeId: int):
    logging.warning("refundPassenjersFee function is not yet implemented")


def routePassenjerJoin(routeId: int, passenjerId: int):
    RoutePassenjer.objects.create(route=routeId, passenjer=passenjerId)
    Route.objects.filter(id=routeId).update(freeSeats=F("freeSeats") - 1)
    logging.info(f"Passenjer joined route {routeId}")


async def notifyPassenjerJoined(routeId: int):
    logging.warning("notifyPassenjerJoined function is not yet implemented")


async def retainPassenjerFee(routeId: int):
    logging.warning("chargePassenjer function is not yet implemented")


def routePassenjerLeave(routeId: int, passenjerId: int):
    RoutePassenjer.objects.filter(route=routeId, passenjerId=passenjerId).delete()
    Route.objects.filter(id=routeId).update(freeSeats=F("freeSeats") + 1)
    logging.info(f"Passenjer leaved route {routeId}")


async def notifyPassenjerLeft(driverId: int):
    logging.warning("notifyPassenjerLeft function is not yet implemented")


async def returnPassenjerFee(routeId: int, passenjerId: int):
    logging.warning("returnPassenjerFee function is not yet implemented")


def finalizeRoute(routeId: int):
    Route.objects.filter(id=routeId).update(finalized=True)
    logging.info(f"The route {routeId} has finalized")


async def notifyRouteFinished(routeId: int):
    logging.info("notifyRouteFinished function is not yet implemented")


async def payDriver(driverId: int):
    logging.info("payDriver function is not yet implemented")
