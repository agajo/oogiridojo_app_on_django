from django.conf.urls import url
from django.contrib.sitemaps.views import sitemap
from .sitemap import sitemaps
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
    url(r'^judger/$', views.JudgerView.as_view(), name='judger'),
    url(r'^yoi_ranking/$', views.YoiView.as_view(), name='yoi_ranking'),
    url(r'^great_answers/$', views.GreatView.as_view(), name='great_answers'),
    url(r'^mypage/$', views.MypageView.as_view(), name='mypage'),
    url(r'^article/$', views.ArticleListView.as_view(), name='article_list'),
    url(r'^article/(?P<pk>[0-9]+)/$', views.ArticleView.as_view(), name='article'),
    url(r'^practice_submit/$', views.practice_submit, name='practice_submit'),
    url(r'^monkasei_yoi_ranking/$', views.MonkaseiYoiRankingView.as_view(), name='monkasei_yoi_ranking'),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps':sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^monkasei_great_ranking/$', views.MonkaseiGreatRankingView.as_view(), name='monkasei_great_ranking'),
    url(r'^recent_answers/$', views.RecentAnswersView.as_view(), name="recent_answers"),
    url(r'^recent_tsukkomi_answers/$', views.RecentTsukkomiAnswersView.as_view(), name="recent_tsukkomi_answers"),
]
