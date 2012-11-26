# Create your views here.

from django.shortcuts import render
from mytardis_hpc_app.form import ContactForm


def index(request):
    if request.method == 'POST': # If the form has been submitted...
        form = ContactForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation ules pass
            # Process the data in form.cleaned_data
            # ...
            return render(request, 'mytardis_hpc_app/submission.html')
    else:
        form = ContactForm() # An unbound form

    return render(request, 'mytardis_hpc_app/index.html', {
        'form': form,
        })


def submission(request):
    return render(request, 'mytardis_hpc_app/submission.html')