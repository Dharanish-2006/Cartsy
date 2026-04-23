from django.core.mail import send_mail
from django.conf import settings

def send_order_confirmation_email(order):
    subject = "🚚 Your Cartsy order is on the way!"

    message = f"""
Hi {order.user.username},

Your order has been successfully confirmed.

Order ID: {order.id}
Total Amount: ₹{order.total_amount}
Payment Method: {order.payment_method}
Status: {order.status}

Thank you for shopping with Cartsy!
"""

    html_content = f"""
    <html>
    <body style="margin:0; padding:0; background:#0B0B1A; font-family:Arial, sans-serif; color:white;">
        
        <div style="max-width:520px; margin:40px auto; padding:30px; background:#111126; border-radius:12px;">
            
            <h1 style="
                text-align:center;
                background: linear-gradient(90deg, #7F5AF0, #FF6AC1);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size:28px;
            ">
                Cartsy
            </h1>

            <h2 style="text-align:center; margin-top:10px;">
                🚚 Your order is on the way!
            </h2>

            <p style="color:#aaa; text-align:center;">
                Hi {order.user.username}, your order has been confirmed.
            </p>

            <div style="
                background:#1A1A2E;
                padding:20px;
                border-radius:10px;
                margin-top:20px;
            ">
                <p><strong>🧾 Order ID:</strong> {order.id}</p>
                <p><strong>💰 Amount:</strong> ₹{order.total_amount}</p>
                <p><strong>💳 Payment:</strong> {order.payment_method}</p>
                <p><strong>📦 Status:</strong> {order.status}</p>
            </div>

            <div style="text-align:center;">
                <a href="https://svs-three.vercel.app/orders" style="
                    display:inline-block;
                    margin-top:25px;
                    padding:12px 24px;
                    border-radius:8px;
                    background: linear-gradient(90deg, #7F5AF0, #FF6AC1);
                    color:white;
                    text-decoration:none;
                    font-weight:bold;
                ">
                    View Order
                </a>
            </div>

            <p style="margin-top:30px; font-size:12px; color:#666; text-align:center;">
                Thanks for shopping with Cartsy 💜
            </p>

        </div>

    </body>
    </html>
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        fail_silently=False,
        html_message=html_content
    )