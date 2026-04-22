import logging
from OrderManagement.models import Order, Notification

logger = logging.getLogger(__name__)


def handle_order_success(order: Order):
    try:
        Notification.objects.create(
            title=f"New Order #{order.id}",
            message=f"{order.user.username} placed an order worth ₹{order.total_amount}",
            type="order",
            order=order,
        )
    except Exception as e:
        logger.error(f"Failed to create notification for order #{order.id}: {e}")

    # Import tasks lazily — avoids crash if Celery/Redis not ready
    try:
        from OrderManagement.tasks import (
            send_admin_email_task,
            send_customer_email_task,
            send_firebase_push_task,
        )
        send_admin_email_task.delay(order.id)
        send_customer_email_task.delay(order.id)
        send_firebase_push_task.delay(order.id)
    except Exception as e:
        logger.error(f"Celery tasks failed for order #{order.id}: {e}")

    _broadcast_ws(order)


def _broadcast_ws(order: Order):
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()
        if channel_layer is None:
            return

        async_to_sync(channel_layer.group_send)(
            "admin_notifications",
            {
                "type": "new_order",
                "order_id": order.id,
                "amount": str(order.total_amount),
                "customer": order.user.username,
            },
        )
    except Exception as e:
        logger.error(f"WS broadcast failed for order #{order.id}: {e}")