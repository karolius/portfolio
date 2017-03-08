from django.conf.urls import url

from .views import (ProductListView,
                    ProductDetailView,
                    ProductCreateView,
                    ProductUpdateView,
                    VariationListView,)

urlpatterns = [
    url(r'^$', ProductListView.as_view(), name='list'),
    url(r'^add/$', ProductCreateView.as_view(), name='add'),
    url(r'^(?P<id>[\w-]+)/$', ProductDetailView.as_view(), name='detail'),
    url(r'^(?P<id>[\w-]+)/edit/$', ProductUpdateView.as_view(), name='edit'),
    url(r'^(?P<id>[\w-]+)/inventory/$', VariationListView.as_view(), name='variation_detail'),
]