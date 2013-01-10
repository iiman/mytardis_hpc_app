from django.test import TestCase
from django.test.client import Client
from flexmock import flexmock
from threading import Thread
from tempfile import mkstemp

from tardis.apps.mytardis_hpc_app.models import ComputationStatus
from tardis.apps.mytardis_hpc_app import views

import os
import urllib2
import base64


class MyTardisHPCAppTest(TestCase):
    def setUp(self):
        self.experiment_id = 1
        self.mytardis_hpc_url = '/apps/mytardis-hpc-app/'
        self.group_id = "TEST_ID000000"

    def test_index(self):
        stages = ['Create', 'Setup', 'Run', 'Terminate']
        self.form_data = {'hpc_apps': 'HRMC',
                          'destination': 'NeCTAR',
                          'stages': stages,
                          'number_of_cores': 1,
                          'group_id': self.group_id}
        index_url = self.mytardis_hpc_url + '%s/' % self.experiment_id

        c = Client()
        response = c.get(index_url)
        self.assertEqual(response.status_code, 200)
        get_content = response.content
        self.assertTrue('Computation submitted to'
                        ' HPC facility' not in get_content)

        fake_request = flexmock(request=lambda: 'requested')
        fake_response = flexmock(read=lambda: 'responded')

        flexmock(views).should_receive('submit_job')\
        .with_args(self.form_data).and_return()
        flexmock(urllib2).should_receive('Request')\
        .and_return(fake_request)
        flexmock(urllib2).should_receive('urlopen')\
        .and_return(fake_response)
        flexmock(Thread).should_receive('start')\
        .and_return(views.submit_job(self.form_data))

        response = c.post(index_url, data=self.form_data)
        self.assertEqual(response.status_code, 200)
        post_content = response.content
        self.assertTrue('Computation submitted to'
                        ' HPC facility' in post_content)
        self.assertTrue('Experiment ID %s'
                        % self.experiment_id in post_content)

        self.form_data['number_of_cores'] = -1
        response = c.post(index_url, data=self.form_data)
        self.assertEqual(response.status_code, 200)
        post_content = response.content
        self.assertTrue('Computation submitted to'
                        ' HPC facility' not in post_content)

    def test_submission(self):
        submission_url = self.mytardis_hpc_url +\
                         '%s/submission/' % self.experiment_id
        c = Client()
        response = c.get(submission_url)
        self.assertEqual(response.status_code, 200)
        get_content = response.content
        self.assertTrue('Experiment ID %s'\
                        % self.experiment_id in get_content)

    def test_response(self):
        response_url = self.mytardis_hpc_url + 'response/'
        values = {'message': 'Stage completed',
                  'stage': 'Create',
                  'group_id': self.group_id}
        c = Client()
        response = c.post(response_url, data=values)
        self.assertEqual(response.status_code, 200)
        computation_list = list(ComputationStatus.objects.filter(
            group_id=self.group_id))
        self.assertEqual(computation_list[0].create_stage, 'completed')
        self.assertNotEqual(computation_list[0].setup_stage, 'completed')

        values['stage'] = 'Setup'
        response = c.post(response_url, data=values)
        self.assertEqual(response.status_code, 200)
        computation_list = list(ComputationStatus.objects.filter(
            group_id=self.group_id))
        self.assertEqual(computation_list[0].create_stage, 'completed')
        self.assertEqual(computation_list[0].setup_stage, 'completed')

        values['stage'] = 'Terminate'
        response = c.post(response_url, data=values)
        self.assertEqual(response.status_code, 200)
        computation_list = list(ComputationStatus.objects.filter(
            group_id=self.group_id))
        self.assertEqual(computation_list[0].terminate_stage, 'completed')

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

    def test_set_computation_status(self):
        current_status = 'completed'
        views.set_computation_status(self.group_id, 'Create', current_status)
        computation_list = list(ComputationStatus.objects.filter(
            group_id=self.group_id))
        stored_status = computation_list[0].create_stage
        self.assertEqual(current_status, stored_status)

        current_status = 'in progress'
        views.set_computation_status(self.group_id, 'Run', current_status)
        computation_list = list(ComputationStatus.objects.filter(
            group_id=self.group_id))
        stored_status = computation_list[0].run_stage
        self.assertEqual(current_status, stored_status)
