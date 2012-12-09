# Create your views here.
import urllib2
from django.shortcuts import render
from django.http import HttpResponse

from tardis.tardis_portal.models.dataset import Dataset
from tardis.tardis_portal.models import Experiment

from tardis.apps.mytardis_hpc_app.form import HPCForm
from tardis.apps.mytardis_hpc_app.response_form import ResponseForm

from django.template import Context, RequestContext, loader
from django.contrib import messages
import json
from tardis.tardis_portal.shortcuts import HttpResponse


receiver = "iimanyusuf@gmail.com"


def index(request, experiment_id):
    print "URL is %s experiment id %s " % (request.path, experiment_id)
    if request.method == 'POST':
        form = HPCForm(request.POST)

        if form.is_valid():
            print 'post request'
            post_request_values = form.cleaned_data
            input_dir_path = get_input_dir_path(experiment_id)
            if input_dir_path:
                encoded_input_dir = encodeZip(input_dir_path)
                post_request_values['input_dir'] = encoded_input_dir
                post_request_values['experiment_id'] = experiment_id

            from threading import Thread
            t = Thread(target=submitjob, args=(post_request_values,))
            t.start()

            template = loader.get_template(
                    'mytardis_hpc_app/submission.html')
            context = RequestContext(request,
                    {'experiment_id': experiment_id,
                     'email':receiver}
                )
            return HttpResponse(template.render(context))
        else:
            print 'invalid post request'
    print 'get requeset'

    form = HPCForm()
    return render(request, 'mytardis_hpc_app/index.html', {
        'form': form,
        'experiment_id': experiment_id,
        })


def encodeZip(zip_file):
    import base64
    f = open(zip_file, "rb")
    b64_text = base64.b64encode(f.read())
    f.close()
    return b64_text


def submitjob(values):
    import urllib
    import urllib2

    url = "http://127.0.0.1:8000/"
    #values=form.cleaned_data

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
        sendEmail(message, receiver)
    return render(request, 'mytardis_hpc_app/response.html', {
        'form':form
            })


def sendEmail(message, receiver) :
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


def results_ready(request, group_id):
    """
    Receive the set of files, retrieve in sequence and add to experiment
    """
    # FIXME: how does it know which experiment?
    res = '""'
    if request.method == 'POST':
        if 'files' in request.POST:
            res = request.POST['files']
        else:
            res = '""'
        if 'experiment_id' in request.POST:
            experiment_id = request.POST['experiment_id']
        else:
            experiment_id = None

    file_list = json.dumps(res)
    ds = _make_data_set(experiment_id)
    # get the output files
    for filename in file_list:
        destination = "http://127.0.0.1:8000/apps/bdphpcprovider/smartconnectorscheduler/" \
            + "/output/%s/%s" % (group_id, filename)
        req = urllib2.Request(destination)
        response = urllib2.urlopen(req)
        text = response.read()
        _make_data_file(ds, filename, text)
        return HttpResponse("",
            mimetype='application/json')


def _make_data_set(exp_id):
     # make datafile
    exp = Experiment.objects.get(id=exp_id)
    dataset = Dataset(description="HRMC results")
    dataset.save()
    dataset.experiments.add(exp)
    dataset.save()
    return dataset


def _make_data_file(dataset, filename, text):
    # TODO:
    # create datasetfile
    # df = models.Dataset_File()
    # df.dataset = dataset
    # df.filename = path.basename(self.file)
    # df.url = 'file://'+self.file
    # df.protocol = "staging"
    # df.size = len(content)
    # df.verify(allowEmptyChecksums=True)
    # df.save()
    # self.df = df
    pass

    # store the key
        #eps, was_created = ExperimentParameterSet.objects.\
        #    get_or_create(experiment=e, schema=key_schema)
        #if was_created:
        #    logger.warn("was created")
        #ep, was_created = ExperimentParameter.objects.get_or_create(parameterset=eps,
        #    name=key_name,
        #    string_value=key_value)
        #if was_created:
        #    logger.warn("was created again")
        #ep.save()



