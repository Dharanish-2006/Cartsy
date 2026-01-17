from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import product, Cart
from OrderManagement.models import Order
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import product
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response

@api_view(["GET"])
@permission_classes([AllowAny])
def HomeAPI(request):
    products = product.objects.all()[:10]
    data = [
        {
            "id": p.id,
            "name": p.product_name,
            "price": p.price,
            "image": p.image.url if p.image else None
        }
        for p in products
    ]
    return Response(data)



class ProductDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        item = product.objects.get(pk=pk)
        serializer = ProductSerializer(item)
        return Response(serializer.data)


class CartAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(items, many=True)
        total = sum(i.total_price for i in items)

        return Response({
            "items": serializer.data,
            "total": total
        })

    def post(self, request):
        product_id = request.data.get("product_id")
        item = product.objects.get(id=product_id)

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=item
        )
        if not created:
            cart_item.quantity += 1
        cart_item.save()

        return Response({"message": "Added to cart"})


class UpdateCartQuantity(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        item_id = request.data.get("item_id")
        action = request.data.get("action")

        item = Cart.objects.get(id=item_id, user=request.user)

        if action == "increase":
            item.quantity += 1
        elif action == "decrease":
            item.quantity -= 1
            if item.quantity == 0:
                item.delete()
                return Response({"message": "Item removed"})

        item.save()
        return Response({"message": "Quantity updated"})



class OrdersAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
