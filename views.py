from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.http.response import JsonResponse
from django.views import generic
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils import timezone
from django.db.models import Sum
import datetime
from .functions import rname

# Create your views here.

from .models import Odai, Answer, Tsukkomi, Judgement, Monkasei, Article, Practice

class IndexView(generic.DetailView):
    model = Odai
    template_name = 'oogiridojo/index.html'
    def get_object(self):
        return Odai.objects.all().order_by('id').last()

class OdaiView(generic.DetailView):
    model = Odai
    #templateはデフォルトでoogiridojo/odai_detail.htmlが使われる。

class JudgementView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'oogiridojo.add_judgement'
    # oogiridojo|judgement|Can add judgement は oogiridojo.add_judgement と書くらしいね。どこで定義されてるんだ。
    model = Odai
    template_name = 'oogiridojo/judgement.html'

class JudgerView(PermissionRequiredMixin, generic.TemplateView):
    permission_required = 'oogiridojo.add_judgement'
    template_name = 'oogiridojo/judger.html'
    def get_context_data(self, **kwargs):
        countall = Judgement.objects.count()
        count1 = Judgement.objects.filter(judgement_score=1).count()
        count2 = Judgement.objects.filter(judgement_score=2).count()
        count3 = Judgement.objects.filter(judgement_score=3).count()
        ratio1 = count1/countall
        ratio2 = count2/countall
        ratio3 = count3/countall
        context = super(JudgerView, self).get_context_data(**kwargs)
        context.update({"countall":countall,
                        "count1":count1,
                        "count2":count2,
                        "count3":count3,
                        "ratio1":ratio1*100,
                        "ratio2":ratio2*100,
                        "ratio3":ratio3*100,
        })
        return context

class YoiView(generic.ListView):
    model = Answer
    template_name = "oogiridojo/yoi_ranking.html"
    def get_queryset(self):
        return Answer.objects.filter(creation_date__gte = timezone.now() - datetime.timedelta(days=7)).order_by('-free_vote_score')[:30]

class GreatView(generic.ListView):
    model = Judgement
    template_name = "oogiridojo/great_answers.html"
    def get_queryset(self):
        return Judgement.objects.filter(judgement_score__exact = 3).order_by('-id')[:30]

def answer_submit(request):
    if(request.get_signed_cookie('monkasei_id',False)):#キーがなかったらエラーではなくFalseを返す
        monkasei_id = request.get_signed_cookie('monkasei_id')
    else:
        monkasei = Monkasei(name = rname())
        monkasei.save()
        monkasei_id = monkasei.id
    answer = Answer(answer_text = request.POST['answer_text'], odai_id = request.POST['odai_id'], monkasei_id = monkasei_id)
    answer.save()
    response = HttpResponseRedirect(reverse('oogiridojo:odai',kwargs={'pk':request.POST['odai_id']}))
    response.set_signed_cookie('monkasei_id', monkasei_id, max_age = 94610000)
    return response

def free_vote(request):
    answer = Answer.objects.get(pk = request.POST['free_vote_button'])
    answer.free_vote_score += 1
    answer.save()
    return JsonResponse({"newscore":answer.free_vote_score})

def tsukkomi_submit(request):
    tsukkomi = Tsukkomi(tsukkomi_text = request.POST['tsukkomi_text'], answer_id = request.POST['answer_id'])
    tsukkomi.save()
    answer = Answer.objects.get(pk=request.POST['answer_id'])
    answer.modified_date = timezone.now()
    answer.save()
    return JsonResponse({"return_tsukkomi":tsukkomi.tsukkomi_text})

@permission_required('oogiridojo.add_judgement')
def judgement_submit(request):
    judgement = Judgement(answer_id = request.POST["answer_id"], judgement_text = request.POST['judgement_text'], judgement_score = request.POST['judgement_score'])
    judgement.save()
    return JsonResponse({"score":judgement.judgement_score, "text":judgement.judgement_text})

def voice_toggle(request):
    request.session['voice_toggle'] = request.POST['voice_toggle']
    request.session.set_expiry(2628000)#有効期限一ヶ月にしてみる。
    return HttpResponse(request.session['voice_toggle'])

class MypageView(generic.DetailView):
    model = Monkasei
    template_name = "oogiridojo/mypage.html"
    def get_object(self):
        monkasei_id = self.request.get_signed_cookie('monkasei_id',False)
        if(monkasei_id):
            return Monkasei.objects.filter(answer__creation_date__gte = timezone.now() - datetime.timedelta(days=14)).annotate(free_vote_score=Sum('answer__free_vote_score')).get(id=monkasei_id)
        else:
            return False

class ArticleView(generic.DetailView):
    model = Article

class ArticleListView(generic.ListView):
    model = Article
    def get_queryset(self):
        return Article.objects.all().order_by('id')

def practice_submit(request):
    practice = Practice(answer_text=request.POST['practice_text'], article_id=request.POST['article_id'])
    practice.save()
    return JsonResponse({"return_practice":practice.answer_text})

class MonkaseiYoiRankingView(generic.ListView):
    model = Monkasei
    template_name = "oogiridojo/monkasei_yoi_ranking.html"
    def get_queryset(self):
        monkaseis = Monkasei.objects.filter(answer__creation_date__gte = timezone.now() - datetime.timedelta(days=14)).annotate(free_vote_score=Sum('answer__free_vote_score')).order_by('-free_vote_score')[:3]
        #こんな風にannotate使って、後から処理したフィールド(プロパティ・属性)加えられるんだね〜
        #filterをannotateの前に入れることで、MonkaseiだけではなくAnswerもフィルタできるらしい。なんか直感と違う。
        for monkasei in monkaseis:
            monkasei.free_vote_score = round(monkasei.free_vote_score,-1)
        return monkaseis
