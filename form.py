from django import forms
from django.forms.fields import ChoiceField, MultipleChoiceField
from django.forms.widgets import CheckboxSelectMultiple

class HPCForm(forms.Form):

    HPC_APPS = ['', 'HRMC']
    hpc_apps = ChoiceField(label="HPC App", required=True, choices=[(x, x) for x in HPC_APPS])

    HPC_PROVIDERS = ['', 'NeCTAR'] #, 'NCI', 'MASSIVE']
    NECTAR_VM_SIZES = ['', 'small', 'medium', 'large', 'extra large']
    destination = ChoiceField(required=True, choices=[(x, x) for x in HPC_PROVIDERS])

    STAGES = ['Create', 'Setup', 'Run', 'Terminate']
    stages = MultipleChoiceField(required=True,
        choices=[(x, x) for x in STAGES],
        widget=CheckboxSelectMultiple)

    number_of_cores = forms.IntegerField(min_value=1)
    group_id = forms.CharField(label="Group ID")