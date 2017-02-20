from django.views.generic import ListView
from .models import Product


class ProductListView(ListView):
    model = Product