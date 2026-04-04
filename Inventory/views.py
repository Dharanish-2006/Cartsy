import razorpay
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from OrderManagement.models import Order, OrderItem, Payment
from OrderManagement.utils.email import send_order_confirmation_email
from .models import product, Cart
from .serializers import ProductSerializer, CartSerializer, OrderSerializer


def _cart_total(cart_items):
    total = sum(Decimal(str(item.total_price)) for item in cart_items)
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)



@api_view(["GET"])
def PublicHomeAPI(request):
    products = product.objects.all()[:10]
    return Response([
        {
            "id": p.id,
            "product_name": p.product_name,
            "price": p.price,
            "image": p.image.url if p.image else None,
        }
        for p in products
    ])


@api_view(["GET"])
def PublicProductDetailAPI(request, pk):
    try:
        item = product.objects.get(pk=pk)
    except product.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    return Response(ProductSerializer(item).data)


class ProductDetailAPI(APIView):
    def get(self, request, pk):
        try:
            item = product.objects.get(pk=pk)
        except product.DoesNotExist:
            return Response({"error": "Not found"}, status=404)
        return Response(ProductSerializer(item).data)



class CartAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Cart.objects.filter(user=request.user).select_related("product")
        total = _cart_total(items)
        return Response({
            "items": CartSerializer(items, many=True).data,
            "total": str(total),
        })

    def post(self, request):
        product_id = request.data.get("product_id")
        quantity   = int(request.data.get("quantity", 1))
        item       = get_object_or_404(product, id=product_id)
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=item)
        cart_item.quantity = quantity if created else cart_item.quantity + quantity
        cart_item.save()
        return Response({"message": "Added to cart"})


class UpdateCartQuantity(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        item_id = request.data.get("item_id")
        action  = request.data.get("action")
        item    = get_object_or_404(Cart, id=item_id, user=request.user)

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
class CreateOrderAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data

        required = ["full_name", "address", "city", "postal_code", "country"]
        missing  = [f for f in required if not str(data.get(f, "")).strip()]
        if missing:
            return Response(
                {"error": f"Missing fields: {', '.join(missing)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_items = Cart.objects.filter(user=request.user).select_related("product")
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        total_amount = _cart_total(cart_items)

        order = Order.objects.create(
            user=request.user,
            full_name   = data["full_name"].strip(),
            address     = data["address"].strip(),
            city        = data["city"].strip(),
            postal_code = data["postal_code"].strip(),
            country     = data["country"].strip(),
            total_amount   = total_amount,
            payment_method = "COD",
            payment_status = "SUCCESS",
            status         = "PLACED",
        )

        for item in cart_items:
            OrderItem.objects.create(
                order    = order,
                product  = item.product,
                quantity = item.quantity,
                price    = Decimal(str(item.product.price)),
            )

        cart_items.delete()

        try:
            send_order_confirmation_email(order)
        except Exception:
            pass  

        return Response(
            {"status": "success", "order_id": order.id},
            status=status.HTTP_201_CREATED,
        )

class CreateRazorpayOrderAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data

        required = ["full_name", "address", "city", "postal_code", "country"]
        missing  = [f for f in required if not str(data.get(f, "")).strip()]
        if missing:
            return Response({"error": f"Missing fields: {', '.join(missing)}"}, status=400)

        cart_items = Cart.objects.filter(user=request.user).select_related("product")
        if not cart_items.exists():
            return Response({"error": "Cart empty"}, status=400)

        total_amount = _cart_total(cart_items)
        amount_paise = int(total_amount * 100)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({
            "amount": amount_paise, "currency": "INR", "payment_capture": 1,
        })

        order = Order.objects.create(
            user=request.user,
            full_name   = data["full_name"].strip(),
            address     = data["address"].strip(),
            city        = data["city"].strip(),
            postal_code = data["postal_code"].strip(),
            country     = data["country"].strip(),
            total_amount      = total_amount,
            payment_method    = "ONLINE",
            payment_status    = "PENDING",
            status            = "PLACED",
            razorpay_order_id = razorpay_order["id"],
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order, product=item.product,
                quantity=item.quantity, price=Decimal(str(item.product.price)),
            )

        Payment.objects.create(
            order=order,
            razorpay_order_id=razorpay_order["id"],
            amount=total_amount,
            status="CREATED",
        )

        return Response({
            "key": settings.RAZORPAY_KEY_ID,
            "order_id": razorpay_order["id"],
            "amount": amount_paise,
        })


class VerifyPaymentAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data   = request.data
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id":   data["razorpay_order_id"],
                "razorpay_payment_id": data["razorpay_payment_id"],
                "razorpay_signature":  data["razorpay_signature"],
            })
        except Exception:
            return Response({"error": "Payment verification failed"}, status=400)

        try:
            payment = Payment.objects.get(razorpay_order_id=data["razorpay_order_id"])
        except Payment.DoesNotExist:
            return Response({"error": "Payment record not found"}, status=404)

        payment.razorpay_payment_id = data["razorpay_payment_id"]
        payment.razorpay_signature  = data["razorpay_signature"]
        payment.status = "SUCCESS"
        payment.save()

        order = payment.order
        order.payment_status = "SUCCESS"
        order.status         = "PAID"
        order.save()

        Cart.objects.filter(user=request.user).delete()

        try:
            send_order_confirmation_email(order)
        except Exception:
            pass

        return Response({"message": "Payment successful", "order_id": order.id})


class OrdersAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        return Response(OrderSerializer(orders, many=True).data)


def ping(request):
    return HttpResponse("OK")