# Create your views here.
from django.conf.urls import patterns, url

from tardis.apps.mytardis_hpc_app import views

urlpatterns = patterns('tardis.apps.mytardis_hpc_app',
    url(r'^(?P<experiment_id>\d+)/$', views.index, name='index'),
    url(r'^experiment/(?P<experiment_id>\d+)/mytardis_hpc_app/$', views.submission, name='submission'),
)
