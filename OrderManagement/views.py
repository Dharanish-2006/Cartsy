import razorpay
from OrderManagement.utils.email import send_order_confirmation_email
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from Inventory.models import Cart
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from Inventory.models import product as Product, ProductImage
from .models import Order, OrderItem, Payment
from .forms import ProductForm,ProductImageForm
from OrderManagement.forms import ProductForm, ProductImageFormSet

@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, "OrderManagement/product_list.html", {"products": products})


@login_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save()

            formset = ProductImageFormSet(
                request.POST,
                request.FILES,
                instance=product
            )

            if formset.is_valid():
                formset.save()
                return redirect("product_list")
        else:
            formset = ProductImageFormSet()

    else:
        form = ProductForm()
        formset = ProductImageFormSet()

    return render(request, "OrderManagement/product_form.html", {
        "form": form,
        "formset": formset
    })


@login_required
def product_edit(request, pk):
    item = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=item)
        formset = ProductImageFormSet(
            request.POST,
            request.FILES,
            instance=item
        )

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect("product_list")
        else:
            print(formset.errors)

    else:
        form = ProductForm(instance=item)
        formset = ProductImageFormSet(instance=item)

    return render(request, "OrderManagement/product_edit.html", {
        "form": form,
        "formset": formset
    })

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        return redirect("product_list")
    return render(request, "OrderManagement/product_delete.html", {"product": product})

@login_required
def create_cod_order(request):
    items = Cart.objects.filter(user=request.user)
    if not items.exists():
        return JsonResponse({"status": "error"})

    total = sum(item.total_price for item in items)

    order = Order.objects.create(
        user=request.user,
        full_name=request.session.get("full_name", ""),
        address=request.session.get("address", ""),
        city=request.session.get("city", ""),
        postal_code=request.session.get("postal_code", ""),
        country=request.session.get("country", ""),
        total_amount=total,
        payment_method="COD",
        payment_status="SUCCESS"
    )
    order.status = "CONFIRMED"
    order.save()
    send_order_confirmation_email(order)
    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,
        )

    items.delete()

    return JsonResponse({"status": "success"})


@login_required
def create_razorpay_order(request):
    items = Cart.objects.filter(user=request.user)
    if not items.exists():
        return JsonResponse({"error": "Cart empty"}, status=400)

    total = sum(item.total_price for item in items)
    amount = int(total * 100)

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    razorpay_order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    request.session["razorpay_order_id"] = razorpay_order["id"]
    request.session["order_total"] = total

    return JsonResponse({
        "order_id": razorpay_order["id"],
        "amount": amount,
        "key": settings.RAZORPAY_KEY_ID
    })

@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        data = request.POST

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id": data["razorpay_order_id"],
                "razorpay_payment_id": data["razorpay_payment_id"],
                "razorpay_signature": data["razorpay_signature"],
            })

            items = Cart.objects.filter(user=request.user)
            total = request.session.get("order_total")

            order = Order.objects.create(
                user=request.user,
                total_amount=total,
                payment_method="ONLINE",
                payment_status="SUCCESS",
                status="PAID",
                razorpay_order_id=data["razorpay_order_id"]
            )

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            items.delete()
            send_order_confirmation_email(order)
            return JsonResponse({"status": "success"})

        except Exception as e:
            return JsonResponse({"status": "failed", "error": str(e)})
 
@login_required
def order_success(request):
    return render(request, "order_confirmation.html")