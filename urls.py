from django.conf.urls import url

from . import views

app_name = 'oogiridojo'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^answer_submit/', views.answer_submit, name='answer_submit'),
]
