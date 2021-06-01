from django import forms


class VisitsForm(forms.Form):
    date_since = forms.DateField(required=False)
    date_until = forms.DateField(required=False)
