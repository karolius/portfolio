from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

from orders.views import AddressSelectFormView
from .views import test
from carts.views import CartView, ItemCoutView, CheckoutView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^cart/$', CartView.as_view(), name='cart'),
    url(r'^cart/count/$', ItemCoutView.as_view(), name='item_count'),
    url(r'^cart/checkout/$', CheckoutView.as_view(), name='checkout'),
    url(r'^cart/checkout/address/$', AddressSelectFormView.as_view(), name='order_address'),

    url(r'^$', test, name='home'),
    url(r'^products/', include("products.urls", namespace="products")),
    url(r'^categories/', include("products.urls_categories", namespace="categories")),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
                   + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
