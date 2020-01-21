from django.urls import path
from .views import HomeView, ItemDetailView, checkoutview, add_to_cart, remove_from_cart

app_name = 'core'

urlpatterns = [
	path('', HomeView.as_view(), name='item-list'),
	path('products/<slug>/', ItemDetailView.as_view(), name='product'),
	path('checkout/', checkoutview, name='checkout'),
	path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
	path('remove-from-cart-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
]