import razorpay
from OrderManagement.utils.email import send_order_confirmation_email
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from Inventory.models import Cart
from django.contrib.auth.decorators import login_required
from Inventory.models import product as Product, ProductImage
from .models import Order, OrderItem, Payment
from .forms import ProductForm, ProductImageForm
from OrderManagement.forms import ProductForm, ProductImageFormSet


@login_required
def create_cod_order(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "detail": "POST required"}, status=405)

    items = Cart.objects.filter(user=request.user)
    if not items.exists():
        return JsonResponse({"status": "error", "detail": "Cart is empty"}, status=400)

    total = sum(item.total_price for item in items)

    full_name   = request.POST.get("full_name", "").strip()
    address     = request.POST.get("address", "").strip()
    city        = request.POST.get("city", "").strip()
    postal_code = request.POST.get("postal_code", "").strip()
    country     = request.POST.get("country", "").strip()

    if not all([full_name, address, city, postal_code, country]):
        return JsonResponse({"status": "error", "detail": "All shipping fields are required"}, status=400)

    order = Order.objects.create(
        user=request.user,
        full_name=full_name,
        address=address,
        city=city,
        postal_code=postal_code,
        country=country,
        total_amount=total,
        payment_method="COD",
        payment_status="SUCCESS",
        status="PLACED",
    )

    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,
        )

    items.delete()
    send_order_confirmation_email(order)

    return JsonResponse({"status": "success", "order_id": order.id})


@login_required
def create_razorpay_order(request):
    items = Cart.objects.filter(user=request.user)
    if not items.exists():
        return JsonResponse({"error": "Cart empty"}, status=400)

    total = sum(item.total_price for item in items)
    amount = int(total * 100)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    razorpay_order = client.order.create({"amount": amount, "currency": "INR", "payment_capture": 1})

    # Store minimal info in session for the verify step
    request.session["razorpay_order_id"] = razorpay_order["id"]
    request.session["order_total"] = float(total)

    return JsonResponse({"order_id": razorpay_order["id"], "amount": amount, "key": settings.RAZORPAY_KEY_ID})


@csrf_exempt
def verify_payment(request):
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=405)

    data = request.POST
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": data["razorpay_order_id"],
            "razorpay_payment_id": data["razorpay_payment_id"],
            "razorpay_signature": data["razorpay_signature"],
        })
    except Exception as e:
        return JsonResponse({"status": "failed", "error": str(e)})

    items = Cart.objects.filter(user=request.user)
    total = request.session.get("order_total", 0)

    order = Order.objects.create(
        user=request.user,
        total_amount=total,
        payment_method="ONLINE",
        payment_status="SUCCESS",
        status="PAID",
        razorpay_order_id=data["razorpay_order_id"],
    )

    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,
        )

    items.delete()
    send_order_confirmation_email(order)
    return JsonResponse({"status": "success"})