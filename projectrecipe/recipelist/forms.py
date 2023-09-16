# forms.py
from django import forms

class SendTextForm(forms.Form):
    phone_number = forms.CharField(max_length=10, label='Phone Number')
    carrier = forms.ChoiceField(choices=[('att', 'AT&T'), ('verizon', 'Verizon'), ('tmobile', 'T-Mobile'), ('sprint', 'Sprint')],
                               label='Phone Carrier')
