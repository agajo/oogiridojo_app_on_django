from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.http.response import JsonResponse
from django.views import generic

# Create your views here.

from .models import Odai, Answer, Tsukkomi

class IndexView(generic.ListView):
    model = Odai
    template_name = 'oogiridojo/index.html'
    def get_queryset(self):
        return Odai.objects.all().order_by('id').reverse()

def answer_submit(request):
    answer = Answer(answer_text = request.POST['answer_text'], odai_id = request.POST['odai_id'])
    answer.save()
    return HttpResponseRedirect(reverse('oogiridojo:index'))

def free_vote(request):
    answer = Answer.objects.get(pk = request.POST['free_vote_button'])
    answer.free_vote_score += 1
    answer.save()
    return JsonResponse({"newscore":answer.free_vote_score})

def tsukkomi_submit(request):
    tsukkomi = Tsukkomi(tsukkomi_text = request.POST['tsukkomi_text'], answer_id = request.POST['answer_id'])
    tsukkomi.save()
    return JsonResponse({"return_tsukkomi":tsukkomi.tsukkomi_text})
