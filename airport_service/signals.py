from django.db.models.signals import post_save
from django.dispatch import receiver
from airport_service.models import Order
from airport_service.tasks import send_order_created_email


@receiver(post_save, sender=Order)
def order_created_handler(sender, instance, created, **kwargs):  # noqa
    if created:
        send_order_created_email.delay(instance.user.email, instance.id)
