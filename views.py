# Create your views here.

import json
import urllib
import urllib2
import settings

from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, RequestContext, loader

from tardis.tardis_portal.models.dataset import Dataset
from tardis.apps.mytardis_hpc_app.form import HPCForm
from tardis.apps.mytardis_hpc_app.response_form import ResponseForm
from tardis.tardis_portal.shortcuts import HttpResponse

from tardis.apps.mytardis_hpc_app.models import ComputationStatus



receiver = ""


def index(request, experiment_id):
    print "URL is %s experiment id %s " % (request.path, experiment_id)
    if request.method == 'POST':
        form = HPCForm(request.POST)

        if form.is_valid():
            print 'post request'
            post_request_values = form.cleaned_data
            input_dir_path = get_input_dir_path(experiment_id)
            if input_dir_path:
                encoded_input_dir = encode_zip(input_dir_path)
                post_request_values['input_dir'] = encoded_input_dir

            from threading import Thread
            t = Thread(target=submit_job, args=(post_request_values,))
            t.start()

            template = loader.get_template(
                    'mytardis_hpc_app/submission.html')
            context = RequestContext(request,
                    {'experiment_id': experiment_id,
                     'computation_status': ComputationStatus.objects.all(),
                     'email':receiver}
                )
            return HttpResponse(template.render(context))
        else:
            print 'invalid post request'
    print 'get request'

    form = HPCForm()
    return render(request, 'mytardis_hpc_app/index.html', {
        'form': form,
        'experiment_id': experiment_id,
        'computation_status': ComputationStatus.objects.all(),
        })


def encode_zip(zip_file):
    import base64
    f = open(zip_file, "rb")
    b64_text = base64.b64encode(f.read())
    f.close()
    return b64_text


def submit_job(values):
    url = settings.BDP_HPC_URL
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    the_page = response.read()


def get_input_dir_path(experiment_id):
    dataset_list = Dataset.objects.filter(
        experiments__id=experiment_id,
        description='HRMC')
    if dataset_list:
        dataset = dataset_list[0]
        for dataf in dataset.dataset_file_set.all():
            if 'input.zip' in dataf.filename:
                return dataf.get_absolute_filepath()
    return None


def response(request):
    print "URL is ", request.path
    form = ResponseForm()
    if request.method == 'POST':
        input_parameter = request.POST
        message = input_parameter['message']
        stage = input_parameter['stage']
        group_id = input_parameter['group_id']
        #send_email(message, receiver)
        set_computation_status(group_id, stage, 'completed')
    return render(request, 'mytardis_hpc_app/response.html', {
        'form':form
            })


def send_email(message, receiver) :
    import smtplib
    import string
    subject = "Group ID for BDP computation"
    sender = 'iman.yusuf@rmit.edu.au'
    body = string.join((
        "From: %s" % sender,
        "TO: %s" %receiver,
        "Subject: %s" %subject,
        " ",
        message
        ), "\r\n")
    server = smtplib.SMTP('localhost')
    server.sendmail(sender, receiver, body)
    server.quit()


def submission(request, experiment_id):
    return render(request, 'mytardis_hpc_app/submission.html', {
        'experiment_id': experiment_id,
        })


def set_computation_status(current_id, stage, status):
    record_exists = ComputationStatus.objects.filter(group_id=current_id)
    if not record_exists:
        computation = ComputationStatus(group_id=current_id)
        computation.save()

    computation_list = list(ComputationStatus.objects.filter(
        group_id=current_id))

    if stage.lower() == "create":
        computation_list[0].create_stage = status

    elif stage.lower() == "setup":
        computation_list[0].setup_stage = status

    elif stage.lower() == "run":
        computation_list[0].run_stage = status

    elif stage.lower() == "terminate":
        computation_list[0].terminate_stage = status

    computation_list[0].save()

def results_ready(request, group_id):
    res = '""'
    if request.method == 'POST':
        if 'files' in request.POST:
            res = request.POST['files']
        else:
            res = '""'
    return HttpResponse(json.dumps(res),
        mimetype='application/json')

