from django.test import TestCase
from django.test.client import Client
from flexmock import flexmock
from threading import Thread
from tempfile import mkstemp

from tardis.apps.mytardis_hpc_app.models import ComputationStatus
from tardis.apps.mytardis_hpc_app import views

import urllib2
import base64
import os

class MyTardisHPCAppTest(TestCase):
    def setUp(self):
        stages = ['Create', 'Setup', 'Run', 'Terminate']
        self.form_data = {'hpc_apps':'HRMC',
                          'destination': 'NeCTAR',
                          'stages': stages,
                          'number_of_cores': 1,
                          'group_id': "TEST_ID000000"}

    def test_index(self):
        c = Client()
        response = c.post('/apps/mytardis-hpc-app/1/', data={})
        self.assertEqual(response.status_code, 200)
        get_content = response.content
        self.assertTrue('Computation submitted to HPC facility' not in get_content)

        fake_request = flexmock(request=lambda: 'requested')
        fake_response = flexmock(read=lambda: 'responded')

        flexmock(views).should_receive('submit_job').with_args(self.form_data).and_return()
        flexmock(urllib2).should_receive('Request').and_return(fake_request)
        flexmock(urllib2).should_receive('urlopen').and_return(fake_response)
        flexmock(Thread).should_receive('start').and_return(views.submit_job(self.form_data))

        response = c.post('/apps/mytardis-hpc-app/1/', data=self.form_data)
        self.assertEqual(response.status_code, 200)
        post_content = response.content
        self.assertTrue('Computation submitted to HPC facility' in post_content)

        self.form_data['number_of_cores']=-1
        response = c.post('/apps/mytardis-hpc-app/1/', data=self.form_data)
        self.assertEqual(response.status_code, 200)
        post_content = response.content
        self.assertTrue('Computation submitted to HPC facility' not in post_content)



    def test_encode_zip(self):
        temp_file = mkstemp()
        file_name = temp_file[1]
        file = open(file_name, "w")
        file.write("This is a test file")
        file.close()
        zipped_file = '/tmp/zipped_file.zip'
        os.system("zip %s %s" % (zipped_file, file_name))
        file = open(zipped_file, "rb")
        b64_encoded = base64.b64encode(file.read())
        file.close()
        self.assertEqual(b64_encoded, views.encode_zip(zipped_file))

    def test_submit_job(self):
        pass

    def test_get_input_dir_path(self):
        pass






    '''


    def submit_job(values):
        url = settings.BDP_HPC_URL
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        print 'bout to fail'
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
        """
        Receive the set of files, retrieve in sequence and add to experiment
        """
        res = '""'
        if request.method == 'POST':
            if 'files' in request.POST:
                res = request.POST['files']
                print "Res in MyTardis %s" % res
            else:
                res = '""'
            if 'experiment_id' in request.POST:
                experiment_id = request.POST['experiment_id']
            else:
                experiment_id = None

        file_list = json.loads(res)


        print "File list ---->>>>>>> %s" % repr(file_list)
        ds = _make_data_set(experiment_id)
        print "Dataset ", ds
        # get the output files
        for filename in file_list:
            print "filename %s" % repr(filename)

            url = "%s%s%s/%s/" % (settings.BDP_HPC_URL,
                                  settings.BDP_HPC_OUTPUT_URL,
                                  group_id, filename)
            print "URL in result ready: %s" % url
            req = urllib2.Request(url)
            print "Request --- ", req
            response = urllib2.urlopen(req)
            print "Response ---", response
            text = response.read()
            #print "text ....", text
            _make_data_file(ds, filename, text)



        return HttpResponse("Result ready returned",
            mimetype='text/plain')


    def _make_data_set(exp_id):
    # make datafile
        exp = Experiment.objects.get(id=exp_id)
        print "Experiment ----", exp
        dataset = Dataset(description="HRMC results")
        dataset.save()
        dataset.experiments.add(exp)
        dataset.save()
        return dataset


    def _make_data_file(dataset, filename, content):
        # TODO:
        # create datasetfile

        f = mktemp()
        print "Inside make data file ", f
        open(f, "w+b").write(content)
        df = Dataset_File()
        df.dataset = dataset
        df.filename = filename
        df.url = 'file://'+f
        df.protocol = "staging"
        df.size = len(content)
        df.verify(allowEmptyChecksums=True)
        df.save()
        print "Df ---", df
        #staging.stage_file(f)

    '''





