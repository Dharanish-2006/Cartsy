from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Dashboard, Widget
from Inventory.models import *

@login_required
def dashboard_view(request):
    dashboard, _ = Dashboard.objects.get_or_create(user=request.user)
    widgets = Widget.objects.all()

    query = request.GET.get("q")
    if query:
        products = product.objects.filter(product_name__icontains=query)
    else:
        products = product.objects.all()[:10]

    return render(request, "dashboard.html", {
        "dashboard": dashboard,
        "widgets": widgets,
        "products": products
    })


@login_required
def product_detail(request, pk):
    item = get_object_or_404(product, pk=pk)
    
    if request.method == "POST":
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=item
        )
        if not created:
            cart_item.quantity += 1
        cart_item.save()
        return redirect("cart")

    return render(request, "product_detail.html", {"product": item})
