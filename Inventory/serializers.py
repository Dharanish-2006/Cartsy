from rest_framework import serializers
from .models import *
from OrderManagement.models import Order, OrderItem, Notification

class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
 
    class Meta:
        model  = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'product_count', 'created_at']
 
    def get_product_count(self, obj):
        return obj.products.count()
 
class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model  = ProductImage
        fields = ['id', 'image', 'order']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            url = obj.image.url
            return request.build_absolute_uri(url) if request else url
        return None


class ProductSerializer(serializers.ModelSerializer):
    image       = serializers.SerializerMethodField()
    images      = ProductImageSerializer(many=True, read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    category    = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True,
    )


    class Meta:
        model  = product
        fields = [
            'id', 'product_name', 'description', 'price', 'image',
            'images', 'stock', 'is_in_stock', 'category', 'category_id',
            'created_at',
        ]


    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image:
            url = obj.image.url
            return request.build_absolute_uri(url) if request else url
        return None


class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model  = Cart
        fields = ["id", "product", "quantity"]

class OrderItemSerializer(serializers.ModelSerializer):
    product_name  = serializers.CharField(source="product.product_name", read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model  = OrderItem
        fields = ["product_name", "product_image", "quantity", "price"]

    def get_product_image(self, obj):
        return obj.product.image.url if obj.product.image else None


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model  = Order
        fields = ["id", "created_at", "status", "total_amount", "items"]
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Notification
        fields = ["id", "title", "message", "type", "is_read", "order", "created_at"]