# Create your views here.

from django.shortcuts import render
from django.http import HttpResponse

from tardis.apps.mytardis_hpc_app.form import HPCForm
from tardis.apps.mytardis_hpc_app.response_form import ResponseForm

from django.template import Context, RequestContext, loader
from django.contrib import messages
import json
from tardis.tardis_portal.shortcuts import HttpResponse


receiver = "iimanyusuf@gmail.com"

def index(request, experiment_id):

    print "URL is ", request.path

    if request.method == 'POST':
        form = HPCForm(request.POST)
        if form.is_valid():
            number_of_cores = form.cleaned_data['number_of_cores']
            group_id = form.cleaned_data['group_id']
            selected_stages = form.cleaned_data['stages']

            from threading import Thread
            t= Thread(target=submitjob, args=(form,))
            t.start()

            template = loader.get_template('mytardis_hpc_app/submission.html')
            context = RequestContext(request,
                {'number_of_cores': number_of_cores,
                 'the_page': "empty",
                 'experiment_id': experiment_id,
                 'group_id': group_id,
                 'form':form,
                 'email':receiver}
            )

            return HttpResponse(template.render(context))
    else:
        form = HPCForm() # An unbound form

    return render(request, 'mytardis_hpc_app/index.html', {
        'form': form,
        'experiment_id': experiment_id,
        })

def submitjob(form):
    import urllib
    import urllib2

    url = "http://127.0.0.1:8000/"
    values=form.cleaned_data
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    the_page = response.read()


def response(request):

    print "URL is ", request.path
    form = ResponseForm()
    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            group_id = form.cleaned_data['group_id']
            print "My new Group ID is ", group_id
            sendEmail(group_id, receiver)

    return render(request, 'mytardis_hpc_app/response.html', {'form':form})


def sendEmail(group_id, receiver) :
    import smtplib
    import string
    subject = "Group ID for BDP computation"
    sender = 'iman.yusuf@rmit.edu.au'
    body = string.join((
        "From: %s" % sender,
        "TO: %s" %receiver,
        "Subject: %s" %subject,
        " ",
        "Your group ID is %s" % group_id
        ), "\r\n")
    server = smtplib.SMTP('localhost')
    server.sendmail(sender, receiver, body)
    server.quit()


def submission(request, experiment_id):
    return render(request, 'mytardis_hpc_app/submission.html', {
        'experiment_id': experiment_id,
        })


def results_ready(request, group_id):
    res = '""'
    if request.method == 'POST':
        if 'files' in request.POST:
            res = request.POST['files']
        else:
            res = '""'
    return HttpResponse(json.dumps(res),
        mimetype='application/json')
