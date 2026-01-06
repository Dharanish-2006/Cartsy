from django.forms import ModelForm
from django.forms import inlineformset_factory
from Inventory.models import product, ProductImage
class ProductForm(ModelForm):
    class Meta:
        model = product
        fields = ["product_name", "description", "price", "image"]

class ProductImageForm(ModelForm):
    class Meta:
        model = ProductImage
        fields = ["image"]

ProductImageFormSet = inlineformset_factory(
    product,
    ProductImage,
    form=ProductImageForm,
    extra=3,
    can_delete=True
)
