from django.urls import path, include
from rest_framework.routers import DefaultRouter

from airport_service.views import (
    CrewViewSet,
    OrderViewSet,
    TicketViewSet,
    AirportViewSet,
    FlightViewSet,
    RouteViewSet,
    AirplaneTypeViewSet,
)

app_name = "airport_service"

router = DefaultRouter()

router.register("crews", CrewViewSet, basename="crews")
router.register("orders", OrderViewSet, basename="orders")
router.register("tickets", TicketViewSet, basename="tickets")
router.register("airports", AirportViewSet, basename="airports")
router.register("flights", FlightViewSet, basename="flights")
router.register("routes", RouteViewSet, basename="routes")
router.register(
    "airplane_types",
    AirplaneTypeViewSet,
    basename="airplane_types",
)


urlpatterns = [
    path("", include(router.urls)),
]
