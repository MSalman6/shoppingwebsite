from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


PAYMENT_CHOICES = (
	('S', 'Stripe'),
	('P', 'Paypal')
	)


class CheckoutForm(forms.Form):
	full_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
		'placeholder': 'Enter Full Name'
		}))
	contact_number = forms.CharField(max_length=10)
	contact_email = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
		'placeholder': 'Enter your Email Address'
		}))
	address1 = forms.CharField(widget=forms.TextInput(attrs={
		'placeholder': 'Enter shipping Adress 1'
		}))
	address2 = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'placeholder': 'Enter shipping Adress 2(Optional)'
		}))
	country = CountryField(blank_label='Select Country').formfield(widget=CountrySelectWidget(attrs={
		'class': 'custom-select d-block w-100'
		}))
	zip_number = forms.CharField(max_length=5, widget=forms.TextInput(attrs={
		'placeholder': 'e.g. "12345"',
		'class': 'form-control'
		}))
	same_billing_address = forms.BooleanField(widget=forms.CheckboxInput, required=False)
	save_info = forms.BooleanField(widget=forms.CheckboxInput, required=False)
	payment_option = forms.ChoiceField(widget=forms.RadioSelect(), choices=PAYMENT_CHOICES)