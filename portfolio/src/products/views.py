from django.views.generic import DetailView
from django.views.generic import ListView
from .models import Product


class ProductListView(ListView):
    model = Product


class ProductDetailView(DetailView):
    model = Product

    def get_context_data(self, **kwargs):
        product = self.get_object()
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context["hd_image"] = product.get_image_url(type='hd')
        print("----CONTEXT:     ", context)
        return context