from django.db import models
from authentication.models import User

class Category(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    slug        = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon        = models.CharField(max_length=10, blank=True, default='🛍️')  # emoji icon
    created_at  = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
 
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
 
    def __str__(self):
        return self.name

class product(models.Model):
    product_name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.FloatField()
    image = models.ImageField(upload_to="products/")
    stock        = models.PositiveIntegerField(default=0)
    category     = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='products'
    )
    created_at   = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.product_name
    @property
    def is_in_stock(self):
        return self.stock > 0


class ProductImage(models.Model):
    product = models.ForeignKey(product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/")
    order   = models.PositiveIntegerField(default=0) 
    class Meta:
        ordering = ['order', 'id']
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
