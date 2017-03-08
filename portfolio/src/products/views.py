from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from .forms import ProductModelForm, VariationInventoryFormSet
from .mixins import ProductIdMixin
from .models import Product, Variation, Category


class ProductListView(ListView):
    model = Product

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        context["object_list"] = self.model.objects.all()
        return context


class ProductDetailView(ProductIdMixin, DetailView):
    model = Product
    
    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        product = self.get_object()
        context["hd_image"] = product.get_image_url(type='hd')
        context["related"] = self.model.objects.get_related(product)
        return context


class ProductCreateView(ProductIdMixin, CreateView):
    model = Product
    form_class = ProductModelForm

    def form_valid(self, form):
        valid_data = super(ProductCreateView, self).form_valid(form)
        return valid_data


class ProductUpdateView(ProductIdMixin, UpdateView):
    model = Product
    form_class = ProductModelForm


class VariationListView(ListView):
    model = Variation
    template_name = "products/variation_list.html"
    queryset = Variation.objects.all()

    def get_product_by_id(self, **kwargs):
        product_id = self.kwargs.get("id")
        product = get_object_or_404(Product, id=product_id)
        return product

    def get_context_data(self, *args, **kwargs):
        context = super(VariationListView, self).get_context_data(**kwargs)
        context["formset"] = VariationInventoryFormSet(queryset=self.get_queryset())
        return context

    def get_queryset(self, **kwargs):
        product = self.get_product_by_id()
        queryset = None
        if product:
            queryset = Variation.objects.filter(product=product)
        return queryset

    def post(self, request, **kwargs):
        formset = VariationInventoryFormSet(request.POST or None, request.FILES)
        # print(formset.non_form_errors())
        # print(formset.errors)
        if formset.is_valid():
            product = self.get_product_by_id()
            for form in formset:
                new_variation = form.save(commit=False)
                if new_variation.title:
                    new_variation.product = product
                    new_variation.save()
            # todo add info that variations are updated
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        raise Http404


class CategoryListView(ListView):
    model = Category
    template_name = "products/product_list.html"


class CategoryDetailView(DetailView):
    model = Category
    template_name = "products/product_list.html"

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
        category = self.get_object()
        context["object_list"] = category.product_set.all()
        return context