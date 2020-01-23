from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, OrderItem, Order, BillingAddress
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm


class HomeView(ListView):
	model = Item
	paginate_by = 12
	template_name = 'home.html'


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


class ItemDetailView(DetailView):
	model = Item
	template_name = 'product.html'


class CheckoutView(View):
	def get(self, *args, **kwargs):
		form = CheckoutForm()
		context = {
		'form': form
		}
		return render(self.request,  'checkout.html', context)

	def post(self, *args, **kwargs):
		form = CheckoutForm(self.request.POST or None)
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			if form.is_valid():
				full_name = form.cleaned_data.get('full_name')
				contact_number = form.cleaned_data.get('contact_number')
				contact_email = form.cleaned_data.get('contact_email')
				address1 = form.cleaned_data.get('address1')
				address2 = form.cleaned_data.get('address2')
				country = form.cleaned_data.get('country')
				zip_number = form.cleaned_data.get('zip_number')
				same_billing_address = form.cleaned_data.get('same_billing_adress')
				save_info = form.cleaned_data.get('save_info')
				payment_option = form.cleaned_data.get('payment_option')
				billing_address = BillingAdress(
					user = self.request.user,
					full_name = full_name,
					contact_number = contact_number,
					contact_email = contact_email,
					address1 = address1,
					address2 = address2,
					country = country,
					zip_number = zip_number,
					same_billing_address = same_billing_address,
					save_info = save_info,
					payment_option = payment_option,
					)
				billing_address.save()
				order.billing_address = billing_address
				order.save()
				return redirect('core:checkout')

		except ObjectDoesNotExist:
				messages.warning(self.request, "You do not have an active order")
				return redirect("core:order-summary")


class PaymentView(View):
	def get(self, *args, **kwargs):
		return render(self.request, 'payment.html')

	def post(self, *args, **kwargs):
		order = Order.objects.get(user=self.request.user, ordered=False)
		token = self.request.POST.get('stripeToken')
		stripe.Charge.create(
		  amount=2000,
		  currency="usd",
		  source= token,
		  description="My First Test Charge (created for API docs)",
		)


@login_required
def add_to_cart(request, slug):
	item = get_object_or_404(Item, slug=slug)
	order_item, created = OrderItem.objects.get_or_create(
		item = item,
		user = request.user,
		ordered = False
		)
	order_qs = Order.objects.filter(user=request.user, ordered=False)
	if order_qs.exists():
		order = order_qs[0]
		# check if the order item is in the order
		if order.items.filter(item__slug=item.slug).exists():
			order_item.quantity += 1
			order_item.save()
			messages.info(request, "The quantity of this item was updated.")
			return redirect("core:order-summary")
		else:
			messages.info(request, "This item was added to your cart.")
			order.items.add(order_item)
			return redirect("core:order-summary")
	else:
		ordered_date = timezone.now()
		order = Order.objects.create(user=request.user, ordered_date=ordered_date)
		order.items.add(order_item)
		messages.info(request, "This item was added to your cart.")
		return redirect("core:order-summary")

@login_required
def remove_from_cart(request, slug):
	item = get_object_or_404(Item, slug=slug)
	order_qs = Order.objects.filter(
		user=request.user,
		ordered=False
		)
	if order_qs.exists():
		order = order_qs[0]
		if order.items.filter(item__slug=item.slug).exists():
			order_item = OrderItem.objects.filter(
			item=item,
			user=request.user,
			ordered=False
			)[0]
			order.items.remove(order_item)
			messages.info(request, "This item was removed from your cart.")
			return redirect("core:order-summary")
		else:
			messages.info(request, "This item is not in your cart.")
			return redirect("core:product", slug=slug)
	else:
		messages.info(request, "You do not have an active order.")
		return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
	item = get_object_or_404(Item, slug=slug)
	order_qs = Order.objects.filter(
		user=request.user,
		ordered=False
		)
	if order_qs.exists():
		order = order_qs[0]
		if order.items.filter(item__slug=item.slug).exists():
			order_item = OrderItem.objects.filter(
			item=item,
			user=request.user,
			ordered=False
			)[0]
			if order_item.quantity > 1:
				order_item.quantity -= 1
				order_item.save()
			else:
				order.items.remove(order_item)
			messages.info(request, "The quantity of this item was updated.")
			return redirect("core:order-summary")
		else:
			messages.info(request, "This item is not in your cart.")
			return redirect("core:order-summary", slug=slug)
	else:
		messages.info(request, "You do not have an active order.")
		return redirect("core:order-summary", slug=slug)

