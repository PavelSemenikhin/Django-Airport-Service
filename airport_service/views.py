from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet

from airport_service import custom_mixins
from airport_service.models import (
    Crew,
    Ticket,
    Order,
    Airport,
    Flight,
    Route,
    AirplaneType,
)
from airport_service.serializers import (
    CrewReadSerializer,
    CrewCreateSerializer,
    OrderCreateSerializer,
    OrderReadSerializer,
    TicketReadSerializer,
    AirportReadSerializer,
    AirportCreateSerializer,
    FlightCreateSerializer,
    FlightReadSerializer,
    RouteCreateSerializer,
    RouteReadSerializer,
    AirplaneTypeReadSerializer,
    AirplaneTypeCreateSerializer,
)


class CrewViewSet(viewsets.ModelViewSet):
    """Endpoints for creating, listing and updating Crew objects."""

    queryset = Crew.objects.all()
    permission_classes = [IsAdminUser]
    ordering_fields = ["last_name"]
    ordering = ["last_name", "first_name"]
    search_fields = ["last_name", "first_name"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return CrewCreateSerializer
        return CrewReadSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """Authenticated users can view their own orders. Staff sees all."""

    permission_classes = [IsAuthenticated]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    filterset_fields = ["user", "created_at"]
    search_fields = ["user__email"]

    def get_queryset(self):

        # Avoiding warning from swagger documentation
        if getattr(self, "swagger_fake_view", False):
            return Order.objects.none()

        user = self.request.user
        queryset = Order.objects.select_related("user").prefetch_related(
            "tickets__flight"
        )
        if user.is_staff:
            return queryset
        else:
            return queryset.filter(user=user)

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderReadSerializer


class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    """Endpoints for creating, listing and updating Ticket objects."""

    queryset = Ticket.objects.select_related("flight", "order")
    filterset_fields = ["flight", "order"]
    permission_classes = [IsAdminUser]
    serializer_class = TicketReadSerializer
    search_fields = [
        "flight__route__source__name",
        "flight__route__destination__name",
        "order__user__email",
    ]


class AirportViewSet(custom_mixins.AdminOrReadOnly):
    """Endpoints for creating, listing and updating Airport objects."""

    queryset = Airport.objects.all()
    search_fields = ["name", "closest_big_city"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return AirportCreateSerializer
        return AirportReadSerializer


class FlightViewSet(custom_mixins.AdminOrReadOnly):
    """Endpoints for creating, listing and updating Flight objects."""

    queryset = Flight.objects.select_related("route", "airplane").prefetch_related(
        "crew"
    )
    ordering_fields = ["departure_time", "arrival_time"]
    filterset_fields = ["route", "airplane", "departure_time", "arrival_time"]
    search_fields = [
        "route__source__name",
        "route__destination__name",
        "airplane__name",
    ]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return FlightCreateSerializer
        return FlightReadSerializer


class RouteViewSet(custom_mixins.AdminOrReadOnly):
    """Endpoints for creating, listing and updating Route objects."""

    queryset = Route.objects.all()
    filterset_fields = ["source", "destination"]
    ordering_fields = ["source"]
    ordering = ["source"]
    search_fields = ["source__name", "destination__name"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return RouteCreateSerializer
        return RouteReadSerializer


class AirplaneTypeViewSet(ModelViewSet):
    """Endpoints for creating, listing and updating AirplaneType objects."""

    queryset = AirplaneType.objects.all()
    permission_classes = [IsAdminUser]
    filterset_fields = ["name"]
    search_fields = ["name"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return AirplaneTypeCreateSerializer
        return AirplaneTypeReadSerializer
