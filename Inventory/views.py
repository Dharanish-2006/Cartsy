from decimal import Decimal, ROUND_HALF_UP
from threading import Thread
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db import transaction
import razorpay

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

from OrderManagement.models import *
from OrderManagement.services.order_service import handle_order_success
from .models import product, Cart
from .serializers import *

def _cart_total(items):
    total = sum(
        (Decimal(str(item.total_price)) for item in items),
        Decimal("0")
    )
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _send_email_async(order):
    from OrderManagement.utils.email import send_order_confirmation_email
    try:
        send_order_confirmation_email(order)
    except Exception as exc:
        import logging
        logging.getLogger(__name__).error(
            f"Email failed for Order #{order.id}: {exc}"
        )


def send_email_background(order):
    Thread(target=_send_email_async, args=(order,), daemon=True).start()


def _deduct_stock(cart_items):
    """Deduct stock for all cart items atomically. Raises ValueError if insufficient."""
    product_ids = [item.product_id for item in cart_items]
    products = {
        p.id: p
        for p in product.objects.select_for_update().filter(id__in=product_ids)
    }
    for item in cart_items:
        p = products[item.product_id]
        if p.stock < item.quantity:
            raise ValueError(
                f"Only {p.stock} unit(s) of '{p.product_name}' available. "
                f"You requested {item.quantity}."
            )
    for item in cart_items:
        p = products[item.product_id]
        p.stock -= item.quantity
        p.save(update_fields=["stock"])



@api_view(["GET"])
@permission_classes([AllowAny])
def HomeAPI(request):
    products = product.objects.all()[:10]
    data = [
        {
            "id":           p.id,
            "product_name": p.product_name,
            "price":        p.price,
            "image":        request.build_absolute_uri(p.image.url) if p.image else None,
            "stock":        p.stock,
            "is_in_stock":  p.is_in_stock,
        }
        for p in products
    ]
    return Response(data, status=status.HTTP_200_OK)


class ProductDetailAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        item       = get_object_or_404(product, pk=pk)
        serializer = ProductSerializer(item, context={"request": request})
        return Response(serializer.data)


class CartAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items      = Cart.objects.filter(user=request.user).select_related("product").prefetch_related("product__images")
        serializer = CartSerializer(items, many=True, context={"request": request})
        total      = _cart_total(items)
        return Response({"items": serializer.data, "total": str(total)})

    def post(self, request):
        product_id = request.data.get("product_id")
        quantity   = int(request.data.get("quantity", 1))
        item       = get_object_or_404(product, id=product_id)

        existing_qty = Cart.objects.filter(
            user=request.user, product=item
        ).values_list("quantity", flat=True).first() or 0

        if item.stock < existing_qty + quantity:
            return Response(
                {"error": f"Only {item.stock} unit(s) available."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cart_item, created = Cart.objects.get_or_create(
            user=request.user, product=item
        )
        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity
        cart_item.save()

        return Response({"message": "Added to cart"}, status=status.HTTP_200_OK)


class UpdateCartQuantity(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        item_id = request.data.get("item_id")
        action  = request.data.get("action")
        item    = get_object_or_404(Cart, id=item_id, user=request.user)

        if action == "increase":
            if item.product.stock < item.quantity + 1:
                return Response(
                    {"error": f"Only {item.product.stock} unit(s) available."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
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
class CreateOrderAPI(APIView):
    """COD orders — validates and deducts stock atomically."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        required = ["full_name", "address", "city", "postal_code", "country", "payment_method"]
        for field in required:
            if not data.get(field, "").strip():
                return Response(
                    {"error": f"{field} is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        cart_items = Cart.objects.filter(
            user=request.user
        ).select_related("product")

        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        total_amount = _cart_total(cart_items)
        if total_amount <= 0:
            return Response({"error": "Invalid cart total"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                _deduct_stock(cart_items)

                order = Order.objects.create(
                    user=request.user,
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

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        handle_order_success(order)
        send_email_background(order)

        return Response(
            {"status": "success", "order_id": order.id},
            status=status.HTTP_201_CREATED,
        )


class CreateRazorpayOrderAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        required = ["full_name", "address", "city", "postal_code", "country"]
        for field in required:
            if not data.get(field, "").strip():
                return Response(
                    {"error": f"{field} is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        cart_items = Cart.objects.filter(
            user=request.user
        ).select_related("product")

        if not cart_items.exists():
            return Response({"error": "Cart empty"}, status=400)

        for item in cart_items:
            if item.product.stock < item.quantity:
                return Response(
                    {"error": f"Only {item.product.stock} unit(s) of '{item.product.product_name}' available."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        total_amount  = _cart_total(cart_items)
        amount_paise  = int(total_amount * 100)

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        razorpay_order = client.order.create({
            "amount":          amount_paise,
            "currency":        "INR",
            "payment_capture": 1,
        })

        PendingRazorpayOrder.objects.update_or_create(
            razorpay_order_id=razorpay_order["id"],
            defaults={
                "user":         request.user,
                "full_name":    data["full_name"],
                "address":      data["address"],
                "city":         data["city"],
                "postal_code":  data["postal_code"],
                "country":      data["country"],
                "total_amount": total_amount,
            },
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
            return Response(
                {"error": "Payment verification failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            pending = PendingRazorpayOrder.objects.get(
                razorpay_order_id=data["razorpay_order_id"]
            )
        except PendingRazorpayOrder.DoesNotExist:
            return Response(
                {"error": "Order details not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_items = Cart.objects.filter(
            user=request.user
        ).select_related("product")

        try:
            with transaction.atomic():
                _deduct_stock(cart_items)

                order = Order.objects.create(
                    user=request.user,
                    full_name=pending.full_name,
                    address=pending.address,
                    city=pending.city,
                    postal_code=pending.postal_code,
                    country=pending.country,
                    total_amount=pending.total_amount,
                    payment_method="ONLINE",
                    payment_status="SUCCESS",
                    status="PAID",
                    razorpay_order_id=data["razorpay_order_id"],
                )
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        quantity=item.quantity,
                        product=item.product,
                        price=Decimal(str(item.product.price)),
                    )

                Payment.objects.create(
                    order=order,
                    razorpay_order_id=data["razorpay_order_id"],
                    razorpay_payment_id=data["razorpay_payment_id"],
                    razorpay_signature=data["razorpay_signature"],
                    amount=pending.total_amount,
                    status="SUCCESS",
                )

                cart_items.delete()
                pending.delete()

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        handle_order_success(order)
        send_email_background(order)

        return Response({"status": "success", "order_id": order.id})


class OrdersAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders     = Order.objects.filter(user=request.user).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)



class AdminOrderListAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        status_filter = request.query_params.get("status")
        qs = Order.objects.select_related("user").prefetch_related(
            "items__product"
        ).order_by("-created_at")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return Response(OrderSerializer(qs, many=True).data)


class AdminOrderDetailAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        order = get_object_or_404(
            Order.objects.select_related("user").prefetch_related("items__product"),
            pk=pk
        )
        return Response(OrderSerializer(order).data)


class UpdateOrderStatusAPI(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        order      = get_object_or_404(Order, pk=pk)
        new_status = request.data.get("status")
        if new_status not in dict(Order.ORDER_STATUS_CHOICES):
            return Response({"error": "Invalid status"}, status=400)
        order.status = new_status
        order.save()
        return Response({"status": order.status})


class AdminNotificationsAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        notifs = Notification.objects.filter(is_read=False)[:50]
        return Response(NotificationSerializer(notifs, many=True).data)


class MarkNotificationReadAPI(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        notif         = get_object_or_404(Notification, pk=pk)
        notif.is_read = True
        notif.save(update_fields=["is_read"])
        return Response({"status": "marked as read"})
class AdminProductListAPI(APIView):
    """List all products with stock levels."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        products   = product.objects.all().order_by("product_name")
        serializer = ProductSerializer(products, many=True, context={"request": request})
        return Response(serializer.data)
class AdminProductStockAPI(APIView):
    """Get or update stock for a single product."""
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        p          = get_object_or_404(product, pk=pk)
        serializer = ProductSerializer(p, context={"request": request})
        return Response(serializer.data)

    def patch(self, request, pk):
        p         = get_object_or_404(product, pk=pk)
        new_stock = request.data.get("stock")

        if new_stock is None:
            return Response({"error": "stock is required"}, status=400)
        try:
            new_stock = int(new_stock)
            if new_stock < 0:
                raise ValueError
        except (ValueError, TypeError):
            return Response({"error": "stock must be a non-negative integer"}, status=400)

        p.stock = new_stock
        p.save(update_fields=["stock"])
        return Response({
            "id":    p.id,
            "name":  p.product_name,
            "stock": p.stock,
        })

def ping(request):
    return HttpResponse("OK")