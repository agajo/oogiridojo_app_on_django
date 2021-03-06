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
from django.core.exceptions import ValidationError
import datetime
import random
from .functions import rname, great_monkasei_days, yoi_monkasei_days, yoi_answer_days

# Create your views here.

from .models import Odai, Answer, Tsukkomi, Judgement, Monkasei, Article, Practice

class IndexView(generic.TemplateView):
    template_name = 'oogiridojo/index.html'
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['odai'] = Odai.objects.order_by('-id').first()
        context['judgement_list'] = Judgement.objects.filter(judgement_score__exact = 3).order_by('-id')[:5]
        context['answer_list'] = Answer.objects.filter(creation_date__gte = timezone.now() - datetime.timedelta(days=yoi_answer_days)).order_by('-free_vote_score')[:5]
        context['great_monkasei_list'] = Monkasei.objects.filter(answer__judgement__creation_date__gte = timezone.now() - datetime.timedelta(days=great_monkasei_days), answer__judgement__judgement_score__exact = 3).annotate(great_count = Count('answer__judgement'), great_newest = Max('answer__judgement__creation_date')).order_by('-great_count','great_newest')[:2]
        monkaseis = Monkasei.objects.filter(answer__creation_date__gte = timezone.now() - datetime.timedelta(days=yoi_monkasei_days)).annotate(free_vote_score=Sum('answer__free_vote_score')).order_by('-free_vote_score')[:2]
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

class JudgerView(PermissionRequiredMixin, generic.TemplateView):
    permission_required = 'oogiridojo.add_judgement'
    template_name = 'oogiridojo/judger.html'
    def get_context_data(self, **kwargs):
        judgements = Judgement.objects.order_by("-id")[:300]
        countall = judgements.count()
        if(countall == 0):
            countall = 1#これが実行される時、値には意味がないので、なんでもいい。0除算を防いでるだけ。
        count1 = len([j for j in judgements if j.judgement_score==1])
        count2 = len([j for j in judgements if j.judgement_score==2])
        count3 = len([j for j in judgements if j.judgement_score==3])
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
        querySet = Answer.objects.filter(creation_date__gte = datetime.datetime(2018,4,1,tzinfo=timezone.utc)).filter(judgement__isnull = True).order_by("id")[:600]
        #2018,4,1という日付に意味はありません。古すぎる奴を表示したくないだけ。これ以上古い奴はジャッジ対象に表示されなくなる。
        # ↓↓↓ 同じ人からの連投があった時に、極力違う人の投稿をジャッジするための処理↓↓↓
        answer_list = []
        for answer in querySet:
          if answer_list==[]:
            answer_list.append(answer)
          else:
            same_user_count = 0
            for appended_answer in answer_list:
              if appended_answer.monkasei == answer.monkasei or (answer.client_ip != "" and appended_answer.client_ip == answer.client_ip):
                same_user_count = same_user_count +1
                # answer_listに「同じ人」による投稿がいくつあるかカウントしています。
                # 「同じ人」とは、IPが同じか、monkaseiが同じ。
            if same_user_count < 3:# 「同じ人」の回答が3個ある時は、answer_listに加えない。
              answer_list.append(answer)
            if len(answer_list) >= 20:
              break;# answer_listが20個に達したら、querySetの精査をやめる。
        context["answer_list"] = answer_list
        return context

class YoiView(generic.ListView):
    model = Answer
    template_name = "oogiridojo/yoi_ranking.html"
    def get_queryset(self):
        return Answer.objects.filter(creation_date__gte = timezone.now() - datetime.timedelta(days=yoi_answer_days)).order_by('-free_vote_score')[:300]

class GreatView(generic.ListView):
    model = Judgement
    template_name = "oogiridojo/great_answers.html"
    def get_queryset(self):
        return Judgement.objects.filter(judgement_score__exact = 3).order_by('-id')[:300]

class RecentAnswersView(generic.ListView):
    model = Answer
    template_name = "oogiridojo/recent_answers.html"
    def get_queryset(self):
        return Answer.objects.order_by("-creation_date")[:300]

class RecentTsukkomiAnswersView(generic.ListView):
    model = Answer
    template_name = "oogiridojo/recent_tsukkomi_answers.html"
    def get_queryset(self):
        return Answer.objects.filter(tsukkomi__isnull = False).annotate(tsukkomi_newest = Max('tsukkomi__creation_date')).order_by('-tsukkomi_newest')[:300]

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
    try:
        tsukkomi.full_clean()
        tsukkomi.save()
        answer = Answer.objects.get(pk=request.POST['answer_id'])
        answer.modified_date = timezone.now()
        answer.save()#ここの3行は後日消しましょう2017-12-23
        return JsonResponse({"return_tsukkomi":tsukkomi.tsukkomi_text})
    except ValidationError:
        return JsonResponse({"error":"validation error"})
    except:
        return JsonResponse({"error":"unknown error"})

@permission_required('oogiridojo.add_judgement')
def judgement_submit(request):
    judgement = Judgement(answer_id = request.POST["answer_id"], judgement_text = request.POST['judgement_text'], judgement_score = request.POST['judgement_score'])
    try:
        judgement.full_clean()#ローカルのsqliteのために、ここでvalidationして字数過多の時にエラーを返すようにします。
        judgement.save()
        return JsonResponse({"score":judgement.judgement_score, "text":judgement.judgement_text})
    except ValidationError :
        return JsonResponse({"error":"validation error"})
    except:
        return JsonResponse({"error":"unknown error"})

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
        monkaseis = Monkasei.objects.filter(answer__creation_date__gte = timezone.now() - datetime.timedelta(days=yoi_monkasei_days)).annotate(free_vote_score=Sum('answer__free_vote_score')).order_by('-free_vote_score')[:3]
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
        return Monkasei.objects.filter(answer__judgement__creation_date__gte = timezone.now() - datetime.timedelta(days=great_monkasei_days), answer__judgement__judgement_score__exact = 3).annotate(great_count = Count('answer__judgement'), great_newest = Max('answer__judgement__creation_date')).order_by('-great_count','great_newest')[:3]
    #最近の3点ジャッジが多い順
    #同数の場合は、先にそのスコアに達した順、つまり、最後の3点獲得の時刻が小さい順
    #filter関数をチェインするといらんINNER JOINが発生してCOUNTがおかしくなります。一つのfilter内に複数条件書こう。

class AnswerGameView(generic.TemplateView):
    template_name = "oogiridojo/answer_game.html"
    def get_context_data(self, **kwargs):
        if(self.request.get_signed_cookie('monkasei_id',False)):#キーがなかったらエラーではなくFalseを返す
            monkasei = Monkasei.objects.get(pk=self.request.get_signed_cookie('monkasei_id'))
            if(monkasei.ningenryoku > 50):
                play = False#人間力50超過ならプレイ不可
            else:
                play = True#人間力50以下ならプレイ可
        else:
            play = True#門下生データのない人はプレイ可
        context = super(AnswerGameView, self).get_context_data(**kwargs)
        context['play'] = play
        return context

def answer_game_start(request):
    #idは歯抜けの可能性があるので、idをランダム指定ではなく、「何番目」をランダム指定
    count = Odai.objects.aggregate(count=Count('id'))["count"]
    i = random.choice(range(count))
    odai = Odai.objects.order_by("id")[i]
    return JsonResponse({"odai":odai.odai_text,"odai_id":odai.id})

class TsukkomiGameView(generic.TemplateView):
    template_name = "oogiridojo/tsukkomi_game.html"

def tsukkomi_game_start(request):
    #idは歯抜けの可能性があるので、idをランダム指定ではなく、「何番目」をランダム指定
    answer_count=0
    while(answer_count<5):#ほとんどの場合、一発で5以上になるはず。そうでないと、なかなか終わらない処理になっちゃう。
        count = Odai.objects.aggregate(count=Count('id'))["count"]
        i = random.choice(range(0,count))
        odai = Odai.objects.order_by("id")[i]
        answer_count = Answer.objects.filter(odai_id=odai.id).aggregate(count=Count('id'))["count"]
    indexes = random.sample(range(answer_count),5)
    answers = []
    for index in indexes:
        answer = Answer.objects.filter(odai_id=odai.id).order_by('id')[index]
        answers.append({"id":answer.id, "answer_text":answer.answer_text})
    return JsonResponse({
        "odai_id":odai.id,
        "odai":odai.odai_text,
        "answers":answers
        })

def tsukkomi_game_submit(request):
    tsukkomi1 = Tsukkomi(tsukkomi_text = request.POST['answer1'], answer_id = request.POST['aid1'])
    tsukkomi2 = Tsukkomi(tsukkomi_text = request.POST['answer2'], answer_id = request.POST['aid2'])
    tsukkomi3 = Tsukkomi(tsukkomi_text = request.POST['answer3'], answer_id = request.POST['aid3'])
    tsukkomi4 = Tsukkomi(tsukkomi_text = request.POST['answer4'], answer_id = request.POST['aid4'])
    tsukkomi5 = Tsukkomi(tsukkomi_text = request.POST['answer5'], answer_id = request.POST['aid5'])
    try:
        tsukkomi1.full_clean()
        tsukkomi2.full_clean()
        tsukkomi3.full_clean()
        tsukkomi4.full_clean()
        tsukkomi5.full_clean()
        tsukkomi1.save()
        tsukkomi2.save()
        tsukkomi3.save()
        tsukkomi4.save()
        tsukkomi5.save()
        response = JsonResponse({"ok":"投稿しました。"})
    except ValidationError as e:
        response = JsonResponse({"error":"空のツッコミがあるか、長すぎるツッコミがあります。"})
        #full_cleanは、回答が長い以外のValidationErrorも出すけど、まあ可能性として回答が長いしかないでしょう。多分。
    except:
        response = JsonResponse({"error":"長すぎるツッコミがあるか、その他のサーバーエラーです。"})
    return response

class WhiteboardView(generic.DetailView):
    model = Odai
    template_name = "oogiridojo/whiteboard.html"

def answer_submit(request):
    #門下生処理
    if(request.get_signed_cookie('monkasei_id',False)):#キーがなかったらエラーではなくFalseを返す
        monkasei = Monkasei.objects.get(pk=request.get_signed_cookie('monkasei_id'))
    else:
        monkasei = Monkasei(name = rname())
        monkasei.save()

    #投稿処理
    #連投チェック
    same_user_count = 0
    querySet = Answer.objects.order_by("-id")[:20]
    for answer in querySet:
        if monkasei.id == answer.monkasei.id or (answer.client_ip != "" and request.META['REMOTE_ADDR'] == answer.client_ip):
            same_user_count = same_user_count +1
            # querySetに「同じ人」による投稿がいくつあるかカウントしています。
            # 「同じ人」とは、IPが同じか、monkaseiが同じ。

    if(same_user_count<10):#連投数に問題がない場合
        if(monkasei.ningenryoku<=50):#人間力が十分小さい場合
            if("datauri" in request.POST and request.POST['datauri']!=""):
                answer1 = Answer(answer_text = request.POST['answer1'], odai_id = request.POST['odai_id'], monkasei_id = monkasei.id, img_datauri = request.POST['datauri'], client_ip = request.META["REMOTE_ADDR"])
            else:
                answer1 = Answer(answer_text = request.POST['answer1'], odai_id = request.POST['odai_id'], monkasei_id = monkasei.id, client_ip = request.META["REMOTE_ADDR"])
            if("answer2" in request.POST):#answer_gameの場合
                answer2 = Answer(answer_text = request.POST['answer2'], odai_id = request.POST['odai_id'], monkasei_id = monkasei.id, client_ip = request.META["REMOTE_ADDR"])
                answer3 = Answer(answer_text = request.POST['answer3'], odai_id = request.POST['odai_id'], monkasei_id = monkasei.id, client_ip = request.META["REMOTE_ADDR"])
            try:
                answer1.full_clean()
                if("answer2" in request.POST):#answer_gameの場合
                    answer2.full_clean()
                    answer3.full_clean()
                    answer2.save()
                    answer3.save()
                    monkasei.ningenryoku = monkasei.ningenryoku+10
                answer1.save()
                monkasei.ningenryoku = monkasei.ningenryoku+5
                monkasei.save()
                response = JsonResponse({"ok":"投稿しました。"})
            except ValidationError as e:
                response = JsonResponse({"error":"回答が空か、長すぎます。"})
                #full_cleanは、回答が長い以外のValidationErrorも出すけど、まあ可能性として回答が長いしかないでしょう。多分。
            except:
                response = JsonResponse({"error":"回答が長すぎるか、その他のサーバーエラーです。"})
        else:#人間力が大きすぎる場合
            if("datauri" in request.POST and request.POST['datauri']!=""):
                response = JsonResponse({"error":"人間力が高すぎます。別タブで下げてきてください。このタブで移動すると絵が消えます。"})
            else:
                response = JsonResponse({"error":"人間力が高すぎます。「良い」して下げましょう。"})
    else:#連投チェックが通らない場合
        response = JsonResponse({"error":"連続投稿数が上限に達してます。しばらく待ってみて下さい。"})
    response.set_signed_cookie('monkasei_id', monkasei.id, max_age = 94610000)
    return response

class OdaiListView(generic.ListView):
    model = Odai
