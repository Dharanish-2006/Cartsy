from rest_framework import serializers
from .models import product, Cart
from OrderManagement.models import Order, OrderItem


class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = product
        fields = ["id", "product_name", "price", "image"]

    def get_image(self, obj):
        return obj.image.url if obj.image else None


class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = Cart
        fields = ["id", "product", "quantity"]


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ["product", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "created_at", "status", "items"]
