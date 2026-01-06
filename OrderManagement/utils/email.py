from django.core.mail import send_mail
from django.conf import settings

def send_order_confirmation_email(order):
    subject = f"Your Package is out of delivery 🎉"

    message = f"""
Hi {order.user.username},

Your order has been successfully confirmed.

🧾 Order ID: {order.id}
💰 Total Amount: ₹{order.total_amount}
💳 Payment Method: {order.payment_method}
📦 Status: {order.status}

Thank you for shopping with us!

- Cartsy Team
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        fail_silently=False,
    )
