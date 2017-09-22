from django.test import TestCase
from .models import Answer
from django.urls import reverse

# Create your tests here.

def create_answer(answer_text):
    return Answer.objects.create(answer_text=answer_text)

class IndexViewAnswersTests(TestCase):
    def test_no_answers(self):
        response = self.client.get(reverse('oogiridojo:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "回答がありません")
        self.assertQuerysetEqual(response.context['answer_list'],[])

    def test_an_answer(self):
        create_answer(answer_text="ほげほげ")
        response = self.client.get(reverse('oogiridojo:index'))
        self.assertContains(response,"ほげほげ")

    def test_an_answer_with_free_vote_score(self):
        Answer.objects.create(answer_text="ふが", free_vote_score=1)
        response = self.client.get(reverse('oogiridojo:index'))
        self.assertContains(response,"<strong>--1</strong>")

    def test_free_vote_score_increment(self):
        answer = Answer.objects.create(answer_text="ふが", free_vote_score=1)
        response = self.client.post(reverse("oogiridojo:index"), {'free_vote_button':answer.id})
        self.assertContains(response,"<strong>--2</strong>")
