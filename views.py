from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.http.response import JsonResponse
from django.views import generic
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils import timezone
from django.db.models import Sum, Count, Max
from django.contrib import messages
import datetime
from .functions import rname

# Create your views here.

from .models import Odai, Answer, Tsukkomi, Judgement, Monkasei, Article, Practice

class IndexView(generic.TemplateView):
    template_name = 'oogiridojo/index.html'
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['odai'] = Odai.objects.order_by('-id').first()
        context['judgement_list'] = Judgement.objects.filter(judgement_score__exact = 3).order_by('-id')[:5]
        context['answer_list'] = Answer.objects.filter(creation_date__gte = timezone.now() - datetime.timedelta(days=7)).order_by('-free_vote_score')[:5]
        context['great_monkasei_list'] = Monkasei.objects.filter(answer__judgement__creation_date__gte = timezone.now() - datetime.timedelta(days=14), answer__judgement__judgement_score__exact = 3).annotate(great_count = Count('answer__judgement'), great_newest = Max('answer__judgement__creation_date')).order_by('-great_count','great_newest')[:2]
        monkaseis = Monkasei.objects.filter(answer__creation_date__gte = timezone.now() - datetime.timedelta(days=14)).annotate(free_vote_score=Sum('answer__free_vote_score')).order_by('-free_vote_score')[:2]
        #こんな風にannotate使って、後から処理したフィールド(プロパティ・属性)加えられるんだね〜
        #filterをannotateの前に入れることで、MonkaseiだけではなくAnswerもフィルタできるらしい。なんか直感と違う。
        for monkasei in monkaseis:
            monkasei.free_vote_score = round(monkasei.free_vote_score,-1)
        context['yoi_monkasei_list'] = monkaseis
        context['article_list'] =  Article.objects.all().order_by('id')
        return context

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
        monkasei = Monkasei.objects.get(pk=request.get_signed_cookie('monkasei_id'))
    else:
        monkasei = Monkasei(name = rname())
        monkasei.save()
    if(monkasei.ningenryoku<=50):
        answer = Answer(answer_text = request.POST['answer_text'], odai_id = request.POST['odai_id'], monkasei_id = monkasei.id)
        answer.save()
        monkasei.ningenryoku = monkasei.ningenryoku+5
        monkasei.save()
    else:
        messages.info(request, "人間力が高すぎます。良いすると下がります。回答："+request.POST['answer_text'])
    response = HttpResponseRedirect(reverse('oogiridojo:odai',kwargs={'pk':request.POST['odai_id']}))
    response.set_signed_cookie('monkasei_id', monkasei.id, max_age = 94610000)
    return response

def free_vote(request):
    if(request.get_signed_cookie('monkasei_id',False)):#キーがなかったらエラーではなくFalseを返す
        monkasei = Monkasei.objects.get(pk=request.get_signed_cookie('monkasei_id'))
        if(monkasei.ningenryoku>0):
            answer = Answer.objects.get(pk = request.POST['free_vote_button'])
            if(answer.monkasei.id == monkasei.id):
                newscore = "自分の投稿です。"
            else:
                answer.free_vote_score += 1
                answer.save()
                monkasei.ningenryoku = monkasei.ningenryoku-1
                monkasei.save()
                newscore = answer.free_vote_score
        else:
            newscore="人間力が低すぎます。回答の投稿で上がります。"
    else:
        newscore="回答を投稿するのが先です。"
    return JsonResponse({"newscore":newscore})

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
            return Monkasei.objects.get(id=monkasei_id)
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
        #model側で先にfree_vote_scoreフィールド作ろうとしたけど、そういうpythonサイドで先に処理した情報はSQLに反映できない。
        #SQL一発でランキング取得するにはこの方法しかない。
        for monkasei in monkaseis:
            monkasei.free_vote_score = round(monkasei.free_vote_score,-1)
        return monkaseis

class MonkaseiGreatRankingView(generic.ListView):
    model = Monkasei
    template_name = "oogiridojo/monkasei_great_ranking.html"
    def get_queryset(self):
        return Monkasei.objects.filter(answer__judgement__creation_date__gte = timezone.now() - datetime.timedelta(days=14), answer__judgement__judgement_score__exact = 3).annotate(great_count = Count('answer__judgement'), great_newest = Max('answer__judgement__creation_date')).order_by('-great_count','great_newest')[:3]
    #最近の3点ジャッジが多い順
    #同数の場合は、先にそのスコアに達した順、つまり、最後の3点獲得の時刻が小さい順
    #filter関数をチェインするといらんINNER JOINが発生してCOUNTがおかしくなります。一つのfilter内に複数条件書こう。
