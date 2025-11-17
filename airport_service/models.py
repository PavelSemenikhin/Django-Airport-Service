from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created_at"]
        db_table = "orders"

    def __str__(self):
        return f"Users {self.user.email} order."


class Airport(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    closest_big_city = models.CharField(max_length=255, null=False)

    class Meta:
        ordering = ["name", "id"]
        db_table = "airports"

    def __str__(self):
        return f"Airport {self.name}."


class AirplaneType(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)

    class Meta:
        ordering = ["name", "id"]
        db_table = "airplane_types"

    def __str__(self):
        return f"Airplane Type {self.name}."


class Airplane(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    rows = models.IntegerField(null=False)
    seats_in_row = models.IntegerField(null=False)
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)

    class Meta:
        ordering = ["name"]
        db_table = "airplanes"

    def __str__(self):
        return f"Airplane {self.name}."


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="departures"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="arrivals"
    )
    distance = models.IntegerField(null=False)

    class Meta:
        ordering = ["id"]
        db_table = "routes"

    def __str__(self):
        return f"Route {self.source.name} -> {self.destination.name}."


class Crew(models.Model):
    first_name = models.CharField(max_length=255, null=False, blank=False)
    last_name = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        ordering = ["last_name", "first_name"]
        db_table = "crews"

    def __str__(self):
        return f"Crew {self.first_name} {self.last_name}."


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flights")
    airplane = models.ForeignKey(
        Airplane, on_delete=models.CASCADE, related_name="flights"
    )
    departure_time = models.DateTimeField(null=False, blank=False)
    arrival_time = models.DateTimeField(null=False, blank=False)
    crew = models.ManyToManyField(Crew, related_name="flights")

    class Meta:
        ordering = ["id"]
        db_table = "flights"

    def __str__(self):
        return f"Flight {self.route.source.name} -> {self.route.destination.name}."


class Ticket(models.Model):
    row = models.IntegerField(null=False, blank=False)
    seat = models.IntegerField(null=False, blank=False)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        ordering = ["id"]
        db_table = "tickets"
        constraints = [
            models.UniqueConstraint(
                fields=["flight", "row", "seat"], name="unique_ticket_per_seat"
            )
        ]
