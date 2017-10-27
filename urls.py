from django.conf.urls import url

from . import views

app_name = 'oogiridojo'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^odai/(?P<pk>[0-9]+)/judgement/$', views.JudgementView.as_view(), name='judgement'),
    url(r'^odai/(?P<pk>[0-9]+)/$', views.OdaiView.as_view(), name='odai'),
    url(r'^answer_submit/$', views.answer_submit, name='answer_submit'),
    url(r'^free_vote/$', views.free_vote, name='free_vote'),
    url(r'^tsukkomi_submit/$', views.tsukkomi_submit, name='tsukkomi_submit'),
    url(r'^judgement_submit/$', views.judgement_submit, name='judgement_submit'),
    url(r'^voice_toggle/$', views.voice_toggle, name='voice_toggle'),
]
