from django.forms import ModelForm
from .models import *

class product_form(ModelForm):
    class Meta:
        model = product
        fields = '__all__'
