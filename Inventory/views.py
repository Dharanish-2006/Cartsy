from decimal import Decimal, ROUND_HALF_UP
from threading import Thread
from django.conf import settings
from django.shortcuts import get_object_or_404
import razorpay
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from OrderManagement.models import Order, OrderItem, Payment
from .models import product, Cart
from .serializers import *


def _cart_total(items):
    total = sum(
        (Decimal(str(item.total_price)) for item in items),
        Decimal("0"))
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _send_email_async(order):
    from OrderManagement.utils.email import send_order_confirmation_email
    try:
        send_order_confirmation_email(order)
    except Exception as exc:
        import logging
        logging.getLogger(__name__).error(
            f"Order confirmation email failed for Order #{order.id}: {exc}"
        )


def send_email_background(order):
    t = Thread(target=_send_email_async, args=(order,), daemon=True)
    t.start()



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def HomeAPI(request):
    products = product.objects.all()[:10]
    data = [
        {
            "id": p.id,
            "product_name": p.product_name,
            "price": p.price,
            "image": p.image.url if p.image else None,
        }
        for p in products
    ]
    return Response(data, status=status.HTTP_200_OK)


class ProductDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        item = product.objects.get(pk=pk)
        serializer = ProductSerializer(item)
        return Response(serializer.data)


class CartAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Cart.objects.filter(user=request.user).select_related("product")
        serializer = CartSerializer(items, many=True)
        total = _cart_total(items)
        return Response(
            {"items": serializer.data, "total": str(total)},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        product_id = request.data.get("product_id")
        quantity   = int(request.data.get("quantity", 1))

        item = get_object_or_404(product, id=product_id)

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=item,
        )
        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity
        cart_item.save()

        return Response({"message": "Added to cart"}, status=status.HTTP_200_OK)


class CreateOrderAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        required = ["full_name", "address", "city", "postal_code", "country", "payment_method"]
        for field in required:
            if not data.get(field, "").strip():
                return Response(
                    {"error": f"{field} is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        cart_items = Cart.objects.filter(user=user).select_related("product")
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        total_amount = _cart_total(cart_items)
        if total_amount <= 0:
            return Response({"error": "Invalid cart total"}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            user=user,
            full_name=data["full_name"],
            address=data["address"],
            city=data["city"],
            postal_code=data["postal_code"],
            country=data["country"],
            total_amount=total_amount,
            payment_method=data["payment_method"],
            payment_status="PENDING",
            status="PLACED",
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=Decimal(str(item.product.price)),
            )

        cart_items.delete()

        send_email_background(order)

        return Response(
            {"status": "success", "order_id": order.id},
            status=status.HTTP_201_CREATED,
        )


class CreateRazorpayOrderAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        cart_items = Cart.objects.filter(user=user).select_related("product")
        if not cart_items.exists():
            return Response({"error": "Cart empty"}, status=400)

        total_amount = _cart_total(cart_items)
        amount_paise = int(total_amount * 100)

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        razorpay_order = client.order.create({
            "amount":          amount_paise,
            "currency":        "INR",
            "payment_capture": 1,
        })

        order = Order.objects.create(
            user=user,
            full_name=data.get("full_name", ""),
            address=data.get("address", ""),
            city=data.get("city", ""),
            postal_code=data.get("postal_code", ""),
            country=data.get("country", ""),
            total_amount=total_amount,
            payment_method="ONLINE",
            payment_status="PENDING",
            status="PLACED",
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=Decimal(str(item.product.price)),
            )

        Payment.objects.create(
            order=order,
            razorpay_order_id=razorpay_order["id"],
            amount=total_amount,
            status="CREATED",
        )

        return Response({
            "key":      settings.RAZORPAY_KEY_ID,
            "order_id": razorpay_order["id"],
            "amount":   amount_paise,
        })


class VerifyPaymentAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data

        razorpay_client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        try:
            razorpay_client.utility.verify_payment_signature({
                "razorpay_order_id":   data["razorpay_order_id"],
                "razorpay_payment_id": data["razorpay_payment_id"],
                "razorpay_signature":  data["razorpay_signature"],
            })
        except Exception:
            return Response({"error": "Payment verification failed"}, status=400)

        payment = Payment.objects.get(razorpay_order_id=data["razorpay_order_id"])
        payment.razorpay_payment_id = data["razorpay_payment_id"]
        payment.razorpay_signature  = data["razorpay_signature"]
        payment.status = "SUCCESS"
        payment.save()

        order = payment.order
        order.payment_status = "SUCCESS"
        order.status = "PAID"
        order.save()

        send_email_background(order)

        return Response({"message": "Payment successful"})


class UpdateCartQuantity(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        item_id = request.data.get("item_id")
        action  = request.data.get("action")

        item = get_object_or_404(Cart, id=item_id, user=request.user)

        if action == "increase":
            item.quantity += 1
            item.save()
        elif action == "decrease":
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
            else:
                item.delete()
                return Response({"message": "Item removed"})

        return Response({"message": "Quantity updated"})


class OrdersAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


def ping(request):
    return HttpResponse("OK")