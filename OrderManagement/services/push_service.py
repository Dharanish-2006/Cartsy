import logging
logger = logging.getLogger(__name__)

def send_admin_push(order):
    try:
        import firebase_admin
        from firebase_admin import credentials, messaging
        from django.conf import settings

        token = getattr(settings, 'ADMIN_FCM_TOKEN', None)
        creds_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', None)

        if not token or not creds_path:
            logger.warning("Firebase not configured — skipping push notification")
            return

        if not firebase_admin._apps:
            cred = credentials.Certificate(creds_path)
            firebase_admin.initialize_app(cred)

        message = messaging.Message(
            notification=messaging.Notification(
                title="New Order Received 🛒",
                body=f"₹{order.total_amount} from {order.user.username}",
            ),
            data={"order_id": str(order.id)},
            token=token,
        )
        messaging.send(message)

    except Exception as e:
        logger.error(f"Firebase push failed for order #{order.id}: {e}")