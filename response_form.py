from django import forms
from django.forms.fields import ChoiceField, MultipleChoiceField
from django.forms.widgets import CheckboxSelectMultiple

class ResponseForm(forms.Form):
    group_id = forms.CharField(label="Group ID")