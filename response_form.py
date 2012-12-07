from django import forms
from django.forms import widgets
from django.forms.fields import ChoiceField, MultipleChoiceField
from django.forms.widgets import CheckboxSelectMultiple

class ResponseForm(forms.Form):
    group_id = forms.IntegerField(min_value=1, label="Group ID", required=True,  widget=widgets.TextInput(attrs={
        'class': 'required'
    }))