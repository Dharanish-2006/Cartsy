import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings

if not firebase_admin._apps:
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)

def send_admin_push(order):
    token = settings.ADMIN_FCM_TOKEN
    if not token:
        return

    message = messaging.Message(
        notification=messaging.Notification(
            title="New Order Received 🛒",
            body=f"₹{order.total_amount} from {order.user.username}",
        ),
        data={"order_id": str(order.id)},
        token=token,
    )
    messaging.send(message)