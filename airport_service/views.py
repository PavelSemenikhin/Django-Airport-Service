import logging

from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
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
from airport_service.tasks import send_order_created_email

logger = logging.getLogger(__name__)


class CrewViewSet(
    custom_mixins.RedisListCacheMixin,
    viewsets.ModelViewSet,
):
    """Endpoints for creating, listing and updating Crew objects."""

    queryset = Crew.objects.all()
    permission_classes = [IsAdminUser]
    ordering_fields = ["last_name"]
    ordering = ["last_name", "first_name"]
    search_fields = ["last_name", "first_name"]
    cache_key = "crew_list"

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

    def list(self, request, *args, **kwargs) -> Response:
        user = request.user
        cached_key = f"user_orders_{user.id}"
        cached = cache.get(cached_key)

        if cached:
            logger.info("👍👍👍👍Redis: returning cached orders.")
            return Response(cached)

        response = super().list(request, *args, **kwargs)
        cache.set(cached_key, response.data, timeout=60)
        return response

    def perform_create(self, serializer):
        order = serializer.save()
        user_email = self.request.user.email
        logger.info(
            f"👍👍👍👍 Creating order: {order.id} sending task to Celery..."
        )  # noqa

        cache.delete(f"user_orders_{self.request.user.id}")
        cache.delete("ticket_list")
        # Run Celery Task
        send_order_created_email.delay(user_email, order.id)

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


class TicketViewSet(
    custom_mixins.RedisListCacheMixin,
    viewsets.ReadOnlyModelViewSet,
):
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
    cache_key = "ticket_list"
    cache_key_prefix = "ticket_detail"

    def retrieve(self, request, *args, **kwargs):
        return custom_mixins.cached_detail(self, request, *args, **kwargs)


class AirportViewSet(custom_mixins.AdminOrReadOnly):
    """Endpoints for creating, listing and updating Airport objects."""

    queryset = Airport.objects.all()
    search_fields = ["name", "closest_big_city"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return AirportCreateSerializer
        return AirportReadSerializer


class FlightViewSet(
    custom_mixins.RedisListCacheMixin,
    custom_mixins.AdminOrReadOnly,
):
    """Endpoints for creating, listing and updating Flight objects."""

    queryset = Flight.objects.select_related(
        "route",
        "airplane",
    ).prefetch_related("crew")
    ordering_fields = ["departure_time", "arrival_time"]
    filterset_fields = ["route", "airplane", "departure_time", "arrival_time"]
    search_fields = [
        "route__source__name",
        "route__destination__name",
        "airplane__name",
    ]
    cache_key = "flight_list"
    cache_key_prefix = "flight_detail"

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return FlightCreateSerializer
        return FlightReadSerializer

    def retrieve(self, request, *args, **kwargs):
        return custom_mixins.cached_detail(
            self,
            request,
            *args,
            **kwargs,
        )


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
    cache_timeout = 60

    @method_decorator(cache_page(cache_timeout))
    def list(self, request, *args, **kwargs):
        logger.info("👍👍👍👍 Returning cached airplane type list")
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(cache_timeout))
    def retrieve(self, request, *args, **kwargs):
        logger.info("👍👍👍👍 Returning cached airplane type detail")
        return super().retrieve(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return AirplaneTypeCreateSerializer
        return AirplaneTypeReadSerializer
