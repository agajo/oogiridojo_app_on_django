from django.test import TestCase
from .models import Odai, Answer
from django.urls import reverse

# Create your tests here.

class OdaiModelTests(TestCase):
    def test_answer_list_order(self):
        odai = Odai.objects.create(odai_text="odada")
        ans1 = Answer.objects.create(answer_text="ans1", odai_id=1)
        ans2 = Answer.objects.create(answer_text="ans2", odai_id=1)
        ans3 = Answer.objects.create(answer_text="ans3", odai_id=1)
        ans2.answer_text="ans2_2"
        #ポスグレだと、この操作をすることで、取り出される順番が変わることがある。それが発生していないかチェックしている。
        ans2.save()
        self.assertQuerysetEqual(odai.answer_list(),['<Answer: ans1>', '<Answer: ans2_2>','<Answer: ans3>'])


class IndexViewAnswersTests(TestCase):
    def test_no_answers(self):
        Odai.objects.create(odai_text="odaoda")
        response = self.client.get(reverse('oogiridojo:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "回答がありません")
        self.assertQuerysetEqual(response.context['odai_list'],['<Odai: odaoda>'])

    def test_an_answer(self):
        odai = Odai.objects.create(odai_text="oda")
        Answer.objects.create(answer_text="ほげほげ", odai_id = odai.id)
        response = self.client.get(reverse('oogiridojo:index'))
        self.assertContains(response,"ほげほげ")

    def test_an_answer_with_free_vote_score(self):
        odai = Odai.objects.create(odai_text="oda")
        Answer.objects.create(answer_text="ふが", free_vote_score=1, odai_id = odai.id)
        response = self.client.get(reverse('oogiridojo:index'))
        self.assertContains(response,"<strong>--1</strong>")

    def test_free_vote_score_increment(self):
        odai = Odai.objects.create(odai_text="oda")
        answer = Answer.objects.create(answer_text="ふが", free_vote_score=1, odai_id = odai.id)
        response = self.client.post(reverse("oogiridojo:index"), {'free_vote_button':answer.id})
        self.assertContains(response,"<strong>--2</strong>")

    def test_no_odai(self):
        response = self.client.get(reverse('oogiridojo:index'))
        self.assertContains(response,"お題がありません")

    def test_add_an_answer_to_an_odai(self):
        odai = Odai.objects.create(odai_text="oda")
        response = self.client.post(reverse("oogiridojo:answer_submit"), {'odai_id':odai.id, 'answer_text':"あんてき"})
        #↑こいつのレスポンスコードは302が返る。リダイレクト前に一回response返してるのか。
        self.assertEquals(response.status_code,302)
        #なので、あらためてindexを取得し直す。
        response2 = self.client.get(reverse('oogiridojo:index'))
        self.assertContains(response2,"あんてき")
