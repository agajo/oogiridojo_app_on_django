from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Odai, Article

class StaticViewSitemap(Sitemap):
    def items(self):
        return['index','recent_answers','recent_tsukkomi_answers','yoi_ranking','great_answers','monkasei_great_ranking','monkasei_yoi_ranking','mypage','article_list','answer_game']
    def location(self, item):
        return reverse('oogiridojo:'+item)

class OdaiSitemap(Sitemap):
    def items(self):
        return Odai.objects.all()
    def location(self,obj):
        return reverse('oogiridojo:odai', kwargs={'pk':obj.pk})

class ArticleSitemap(Sitemap):
    def items(self):
        return Article.objects.all()
    def location(self,obj):
        return reverse('oogiridojo:article', kwargs={'pk':obj.pk})

sitemaps = {
    'odai':OdaiSitemap,
    'static':StaticViewSitemap,
    'article':ArticleSitemap,
}
