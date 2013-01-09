from django.test import TestCase
from django.test.client import Client
from flexmock import flexmock
from threading import Thread

from tardis.apps.mytardis_hpc_app.models import ComputationStatus
from tardis.apps.mytardis_hpc_app import views

import urllib2


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
        # Testing whether a post request with invalid form
        response = c.post('/apps/mytardis-hpc-app/1/', data={})
        self.assertEqual(response.status_code, 200)

        fake_request = flexmock(request=lambda: 'requested')
        fake_response = flexmock(read=lambda: 'responded')

        flexmock(views).should_receive('submit_job').with_args(self.form_data).and_return()
        flexmock(urllib2).should_receive('Request').and_return(fake_request)
        flexmock(urllib2).should_receive('urlopen').and_return(fake_response)
        flexmock(Thread).should_receive('start').and_return(views.submit_job(self.form_data))

        response = c.post('/apps/mytardis-hpc-app/1/', data=self.form_data)
        self.assertEqual(response.status_code, 200)




