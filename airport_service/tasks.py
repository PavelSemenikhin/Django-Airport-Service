from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_order_created_email(user_email: str, order_id: int):
    subject = "Your Order Confirmation"
    message = f"Your order with ID {order_id} has been successfully created."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)
    print(f"Email sent to {user_email} for order {order_id}")
