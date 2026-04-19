import requests
from django.conf import settings

BREVO_URL = "https://api.brevo.com/v3/smtp/email"

def _brevo_headers():
    return {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": settings.BREVO_API_KEY,
    }

def send_admin_order_email(order):
    items_html = "".join(
        f"<li>{item.product.product_name} × {item.quantity} — ₹{item.price}</li>"
        for item in order.items.all()
    )
    payload = {
        "sender": {"name": "Cartsy Alerts", "email": settings.DEFAULT_FROM_EMAIL},
        "to": [{"email": settings.ADMIN_EMAIL}],
        "subject": f"🛒 New Order #{order.id} — ₹{order.total_amount}",
        "htmlContent": f"""
            <h2>New Order Received</h2>
            <p><strong>Customer:</strong> {order.user.username} ({order.user.email})</p>
            <p><strong>Total:</strong> ₹{order.total_amount}</p>
            <p><strong>Payment:</strong> {order.payment_method}</p>
            <ul>{items_html}</ul>
            <a href="{settings.ADMIN_DASHBOARD_URL}/orders/{order.id}" 
               style="background:#7c6aff;color:white;padding:10px 20px;border-radius:8px;text-decoration:none;">
              View Order →
            </a>
        """,
    }
    resp = requests.post(BREVO_URL, json=payload, headers=_brevo_headers())
    resp.raise_for_status()

def send_customer_confirmation_email(order):
    payload = {
        "sender": {"name": "Cartsy", "email": settings.DEFAULT_FROM_EMAIL},
        "to": [{"email": order.user.email}],
        "subject": f"Order Confirmed #{order.id} 🎉",
        "htmlContent": f"""
            <h2>Thanks for your order, {order.user.username}!</h2>
            <p>Order <strong>#{order.id}</strong> — ₹{order.total_amount}</p>
            <p>We'll notify you when it ships.</p>
        """,
    }
    resp = requests.post(BREVO_URL, json=payload, headers=_brevo_headers())
    resp.raise_for_status()