from rest_framework import serializers
from .models import *
from OrderManagement.models import Order, OrderItem


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image"]

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = product
        fields = ["id", "product_name", "price", "image", "images", "description"]

    def get_image(self, obj):
        return obj.image.url if obj.image else None


class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = Cart
        fields = ["id", "product", "quantity"]

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.product_name", read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["product_name", "product_image", "quantity", "price"]

    def get_product_image(self, obj):
        return obj.product.image.url if obj.product.image else None


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "created_at", "status", "total_amount", "items"]
