from django.conf.urls import url

from . import views

app_name = 'oogiridojo'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^answer_submit/', views.answer_submit, name='answer_submit'),
    url(r'^free_vote/', views.free_vote, name='free_vote'),
]
