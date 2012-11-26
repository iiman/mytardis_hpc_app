# Create your views here.
from django.conf.urls import patterns, url

from mytardis_hpc_app import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^$', views.submission, name='submission'),
)