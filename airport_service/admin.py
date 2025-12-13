from django.contrib import admin

from airport_service.models import (
    Order,
    Airport,
    Airplane,
    AirplaneType,
    Route,
    Crew,
    Flight,
    Ticket,
)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    search_fields = ("user", "created_at")


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("name", "closest_big_city")
    search_fields = ("name", "closest_big_city")


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ("name", "rows", "seats_in_row", "airplane_type")
    search_fields = ("name", "rows", "seats_in_row", "airplane_type")


@admin.register(AirplaneType)
class AirplaneTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("source", "destination", "distance")
    search_fields = ("source__name", "destination__name", "distance")


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
    )
    search_fields = ("first_name", "last_name")


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("route", "airplane", "departure_time", "arrival_time")
    search_fields = ("route__source__name", "airplane__name")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("row", "seat", "flight", "order")
    search_fields = ("flight__route__source__name", "order__user__email")
