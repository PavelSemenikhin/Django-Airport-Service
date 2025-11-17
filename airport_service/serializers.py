from django.db import transaction
from poetry.console.commands import self
from rest_framework import serializers

from airport_service.models import (
    Order,
    Ticket,
    Airport,
    AirplaneType,
    Airplane,
    Route,
    Crew,
    Flight,
)


class CrewReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class CrewCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")
        read_only_fields = ("id",)


class TicketNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "flight", "seat")
        read_only_fields = ("id",)


class TicketReadSerializer(serializers.ModelSerializer):
    order = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order")
        read_only_fields = ("id",)


class AirportReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")
        read_only_fields = ("id",)


class AirportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")
        read_only_fields = ("id",)


class AirplaneTypeReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneTypeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")
        read_only_fields = ("id",)


class AirplaneReadSerializer(serializers.ModelSerializer):
    airplane_type = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")


class AirplaneCreateSerializer(serializers.ModelSerializer):
    airplane_type = serializers.PrimaryKeyRelatedField(
        queryset=AirplaneType.objects.all()
    )

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")
        read_only_fields = ("id",)


class RouteReadSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(slug_field="name", read_only=True)
    destination = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")
        read_only_fields = ("id",)


class RouteCreateSerializer(serializers.ModelSerializer):
    source = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all())
    destination = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all())

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")
        read_only_fields = ("id",)


class FlightReadSerializer(serializers.ModelSerializer):
    crew = serializers.SlugRelatedField(
        slug_field="first_name", read_only=True, many=True
    )
    route = serializers.SlugRelatedField(slug_field="id", read_only=True)
    airplane = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew")


class FlightCreateSerializer(serializers.ModelSerializer):
    route = serializers.PrimaryKeyRelatedField(queryset=Route.objects.all())
    airplane = serializers.PrimaryKeyRelatedField(queryset=Airplane.objects.all())
    crew = serializers.PrimaryKeyRelatedField(queryset=Crew.objects.all(), many=True)

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew")
        read_only_fields = ("id",)


class OrderReadSerializer(serializers.ModelSerializer):
    tickets = TicketReadSerializer(many=True, read_only=True)
    user = serializers.SlugRelatedField(slug_field="email", read_only=True)

    class Meta:
        model = Order
        fields = ("id", "created_at", "user", "tickets")
        read_only_fields = ("id",)


class OrderCreateSerializer(serializers.ModelSerializer):
    tickets = TicketNestedSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ("id", "created_at", "user", "tickets")
        read_only_fields = ("id", "created_at", "user")

    def create(self, validated_data):
        user = self.context["request"].user
        tickets_data = validated_data.pop("tickets", [])

        with transaction.atomic():
            order = Order.objects.create(user=user, **validated_data)

            for ticket in tickets_data:
                flight = ticket["flight"]
                row = ticket["row"]
                seat = ticket["seat"]

                if Ticket.objects.filter(flight=flight, row=row, seat=seat).exists():
                    raise serializers.ValidationError(
                        f"Seat {row}-{seat} on flight {flight.id} already taken."
                    )

                Ticket.objects.create(order=order, **ticket)
            return order
