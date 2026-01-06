from django.db import models
from authentication.models import User

class product(models.Model):
    product_name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.FloatField()
    image = models.ImageField(upload_to="products/")
    def __str__(self):
        return self.product_name


class ProductImage(models.Model):
    product = models.ForeignKey(product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/")
    def __str__(self):
        return f"{self.product.product_name} - Image"
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
    product = models.ForeignKey(product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    @property
    def total_price(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return f"{self.user.username} - {self.product.product_name} ({self.quantity})"
