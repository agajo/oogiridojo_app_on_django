from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

# Create your views here.

from .models import Answer

def index(request):
    if('free_vote_button' in request.POST):
        answer = Answer.objects.get(pk=request.POST['free_vote_button'])
        answer.free_vote_score += 1
        answer.save()
    answer_list = Answer.objects.all()
    context = {'answer_list': answer_list}
    return render(request, 'oogiridojo/index.html', context)

def answer_submit(request):
    answer = Answer(answer_text = request.POST['answer_text'])
    answer.save()
    return HttpResponseRedirect(reverse('oogiridojo:index'))
