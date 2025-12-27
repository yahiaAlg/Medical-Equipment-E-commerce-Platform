from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Fieldset, Div, HTML
from .models import Order

class CheckoutForm(forms.Form):
    # Shipping Information
    shipping_address = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Shipping Address'
    )
    shipping_city = forms.CharField(max_length=100, label='City')
    shipping_state = forms.CharField(max_length=100, label='State/Province')
    shipping_zip = forms.CharField(max_length=10, label='ZIP/Postal Code')
    shipping_country = forms.CharField(max_length=100, label='Country')
    
    # Billing Information
    same_as_shipping = forms.BooleanField(
        required=False,
        initial=True,
        label='Billing address is the same as shipping address'
    )
    billing_address = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Billing Address',
        required=False
    )
    billing_city = forms.CharField(max_length=100, label='City', required=False)
    billing_state = forms.CharField(max_length=100, label='State/Province', required=False)
    billing_zip = forms.CharField(max_length=10, label='ZIP/Postal Code', required=False)
    billing_country = forms.CharField(max_length=100, label='Country', required=False)
    
    # Payment Information
    payment_method = forms.ChoiceField(
        choices=Order.PAYMENT_METHODS,
        widget=forms.RadioSelect,
        label='Payment Method'
    )
    
    # Special Instructions
    special_instructions = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label='Special Delivery Instructions'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Shipping Information',
                'shipping_address',
                Row(
                    Column('shipping_city', css_class='form-group col-md-4 mb-3'),
                    Column('shipping_state', css_class='form-group col-md-4 mb-3'),
                    Column('shipping_zip', css_class='form-group col-md-4 mb-3'),
                ),
                'shipping_country',
            ),
            
            Fieldset(
                'Billing Information',
                'same_as_shipping',
                Div(
                    'billing_address',
                    Row(
                        Column('billing_city', css_class='form-group col-md-4 mb-3'),
                        Column('billing_state', css_class='form-group col-md-4 mb-3'),
                        Column('billing_zip', css_class='form-group col-md-4 mb-3'),
                    ),
                    'billing_country',
                    css_id='billing-fields'
                ),
            ),
            
            Fieldset(
                'Payment Method',
                'payment_method',
            ),
            
            Fieldset(
                'Additional Information',
                'special_instructions',
            ),
            
            Submit('submit', 'Continue to Review', css_class='btn btn-primary btn-lg w-100')
        )
        
        # Add Bootstrap classes
        for field in self.fields:
            if field not in ['same_as_shipping', 'payment_method']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        cleaned_data = super().clean()
        same_as_shipping = cleaned_data.get('same_as_shipping')
        
        if same_as_shipping:
            # Copy shipping data to billing fields
            cleaned_data['billing_address'] = cleaned_data.get('shipping_address')
            cleaned_data['billing_city'] = cleaned_data.get('shipping_city')
            cleaned_data['billing_state'] = cleaned_data.get('shipping_state')
            cleaned_data['billing_zip'] = cleaned_data.get('shipping_zip')
            cleaned_data['billing_country'] = cleaned_data.get('shipping_country')
        else:
            # Validate billing fields are provided
            billing_fields = ['billing_address', 'billing_city', 'billing_state', 'billing_zip', 'billing_country']
            for field in billing_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, 'This field is required when billing address is different from shipping.')
        
        return cleaned_data