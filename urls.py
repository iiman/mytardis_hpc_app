# Create your views here.
from django.conf.urls import patterns, url

from tardis.apps.mytardis_hpc_app import views


urlpatterns = patterns('tardis.apps.mytardis_hpc_app',
    url(r'^(?P<experiment_id>\d+)/$', views.index, name='index'),
    url(r'^(?P<experiment_id>\d+)/submission/$', views.submission, name='submission'),
    url(r'^response/$', views.response, name='response'),
    url(r'^resultsready/(?P<group_id>\w+)/$', views.results_ready, name="results_ready")
)
