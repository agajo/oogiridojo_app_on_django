from django.test import TestCase, Client
from .models import Odai, Answer, Tsukkomi, Judgement
from django.urls import reverse
from django.contrib.auth.models import User, Permission

# Create your tests here.

class OdaiModelTests(TestCase):
    def test_answer_list_order(self):
        odai = Odai.objects.create(id = 1, odai_text="test_answer_list_order")
        ans1 = Answer.objects.create(answer_text="ans1", odai_id=1, modified_date="2017-01-01T01:01:03")
        ans2 = Answer.objects.create(answer_text="ans2", odai_id=1, modified_date="2017-01-01T01:01:03")
        ans3 = Answer.objects.create(answer_text="ans3", odai_id=1, modified_date="2017-01-01T01:01:03")
        ans2.answer_text="ans2_2"
        #ポスグレだと、この操作をすることで、取り出される順番が変わることがある。それが発生していないかチェックしている。
        ans2.save()
        self.assertQuerysetEqual(odai.answer_list(),['<Answer: ans3>', '<Answer: ans2_2>','<Answer: ans1>'])
        #最新の投稿を先に表示します。

    def test_answer_list_order_with_modified_date(self):
        odai = Odai.objects.create(id = 1, odai_text="answer_list_order_with_modified_date")
        ans1 = Answer.objects.create(answer_text="ans1", odai_id=1, modified_date="2017-01-01T01:01:03")
        ans2 = Answer.objects.create(answer_text="ans2", odai_id=1, modified_date="2017-01-01T01:01:04")
        ans3 = Answer.objects.create(answer_text="ans3", odai_id=1, modified_date="2017-01-01T01:01:03")
        self.assertQuerysetEqual(odai.answer_list(),['<Answer: ans2>', '<Answer: ans3>','<Answer: ans1>'])

    def test_number_one_answer(self):
        odai = Odai.objects.create(id=1, odai_text="test_number_one_answer")
        ans1 = Answer.objects.create(answer_text="ans1", odai_id=1, free_vote_score=1)
        ans2 = Answer.objects.create(answer_text="ans2", odai_id=1, free_vote_score=300)
        ans3 = Answer.objects.create(answer_text="ans3", odai_id=1, free_vote_score=50)
        anslist = odai.answer_list()
        self.assertFalse(anslist[0].is_number_one)
        self.assertTrue(anslist[1].is_number_one)
        self.assertFalse(anslist[2].is_number_one)

class IndexViewTests(TestCase):
    def test_only_one_newest_odai_shown(self):
        odai1 = Odai.objects.create(odai_text="test_odai_order1")
        odai2 = Odai.objects.create(odai_text="test_odai_order2")
        response = self.client.get(reverse('oogiridojo:index'))
        self.assertQuerysetEqual(response.context['odai_list'],['<Odai: test_odai_order2>'])

    def test_no_odai(self):
        response = self.client.get(reverse('oogiridojo:index'))
        self.assertContains(response,"お題がありません")

class OdaiViewAnswersTests(TestCase):
    def test_no_answers(self):
        odai = Odai.objects.create(odai_text="odaoda")
        response = self.client.get(reverse('oogiridojo:odai',kwargs={'pk':odai.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "回答がありません")

    def test_an_answer(self):
        odai = Odai.objects.create(odai_text="oda")
        Answer.objects.create(answer_text="ほげほげ", odai_id = odai.id)
        response = self.client.get(reverse('oogiridojo:odai',kwargs={'pk':odai.id}))
        self.assertContains(response,"ほげほげ")

    def test_an_answer_with_free_vote_score(self):
        odai = Odai.objects.create(odai_text="oda")
        Answer.objects.create(answer_text="ふが", free_vote_score=1, odai_id = odai.id)
        response = self.client.get(reverse('oogiridojo:odai',kwargs={'pk':odai.id}))
        self.assertContains(response,'<strong class="free_vote_score">1</strong>')

    def test_an_answer_with_tsukkomi(self):
        odai = Odai.objects.create(odai_text="oda")
        answer = Answer.objects.create(answer_text="ふが", odai_id = odai.id)
        tsukkomi = Tsukkomi.objects.create(tsukkomi_text="つっこみます", answer_id=answer.id)
        response = self.client.get(reverse('oogiridojo:odai',kwargs={'pk':odai.id}))
        self.assertContains(response,"つっこみます")

    def test_free_vote_score_increment(self):
        odai = Odai.objects.create(odai_text="oda")
        answer = Answer.objects.create(answer_text="ふが", free_vote_score=1, odai_id = odai.id)
        response = self.client.post(reverse("oogiridojo:free_vote"), {'free_vote_button':answer.id})
        self.assertEqual(response.json()["newscore"], 2)

    def test_tsukkomi_submit(self):
        odai = Odai.objects.create(odai_text="oda")
        answer = Answer.objects.create(answer_text="ふが", free_vote_score=1, odai_id = odai.id)
        response = self.client.post(reverse("oogiridojo:tsukkomi_submit"), {'answer_id':answer.id, 'tsukkomi_text':"つっこみ"})
        self.assertEqual(response.json()["return_tsukkomi"],"つっこみ")

    def test_tsukkomi_submit_and_modify_answer_date(self):
        odai = Odai.objects.create(odai_text="oda")
        answer1 = Answer.objects.create(answer_text="ans1", odai_id = odai.id, modified_date="2017-01-01T01:01:01")
        answer2 = Answer.objects.create(answer_text="ans2", odai_id = odai.id, modified_date="2017-01-01T01:01:01")
        answer3 = Answer.objects.create(answer_text="ans3", odai_id = odai.id, modified_date="2017-01-01T01:01:01")
        response = self.client.post(reverse("oogiridojo:tsukkomi_submit"), {'answer_id':answer2.id, 'tsukkomi_text':"つっこみ"})
        self.assertQuerysetEqual(odai.answer_list(),['<Answer: ans2>', '<Answer: ans3>','<Answer: ans1>'])

    def test_add_an_answer_to_an_odai(self):
        odai = Odai.objects.create(odai_text="oda")
        response = self.client.post(reverse("oogiridojo:answer_submit"), {'odai_id':odai.id, 'answer_text':"あんてき"})
        #↑こいつのレスポンスコードは302が返る。
        #redirectのレスポンスを受け取って、クライアントがそのURLに改めてリクエストを出すからね。
        self.assertRedirects(response,reverse('oogiridojo:odai',kwargs={'pk':odai.id}))
        #なので、あらためてindexを取得し直す。
        response2 = self.client.get(reverse('oogiridojo:odai',kwargs={'pk':odai.id}))
        self.assertContains(response2,"あんてき")

    def test_show_judgement(self):
        odai = Odai.objects.create(odai_text="ジャッジあり")
        answer = Answer.objects.create(answer_text="あご", odai_id = odai.id)
        judgement = Judgement.objects.create(judgement_score=1, judgement_text="いいね", answer_id=answer.id)
        response = self.client.get(reverse('oogiridojo:odai',kwargs={'pk':odai.id}))
        self.assertContains(response,"1点。")
        self.assertContains(response,"いいね")

    def test_show_judgement_link_with_permission(self):
        odai = Odai.objects.create(odai_text="うで")
        user = User.objects.create_user("judger", password="hoge")
        permission = Permission.objects.get(codename='add_judgement')
        user.user_permissions.add(permission)
        c = Client()
        c.login(username="judger", password="hoge")
        response = c.get(reverse('oogiridojo:odai',kwargs={'pk':odai.id}))
        self.assertContains(response,'ジャッジ</a>')

    def test_not_show_judgement_link_without_permission(self):
        odai = Odai.objects.create(odai_text="うで")
        user = User.objects.create_user("judger", password="hoge")
        c = Client()
        c.login(username="judger", password="hoge")
        response = c.get(reverse('oogiridojo:odai',kwargs={'pk':odai.id}))
        self.assertNotContains(response,'ジャッジ</a>')

class JudgementViewTests(TestCase):
    def test_no_permission(self):
        odai = Odai.objects.create(odai_text="ッジ")
        response = self.client.get(reverse('oogiridojo:judgement',kwargs={'pk':odai.id}))
        # パーミッションがない場合はログインページに飛ばされる。
        self.assertRedirects(response, reverse('accounts:login')+"?next=/oogiridojo/odai/"+str(odai.id)+"/judgement/")
        # nextパラメータが付くので注意

    def test_with_permission(self):
        odai = Odai.objects.create(odai_text="ッジ")
        user = User.objects.create_user(username="judger", password="hoge")
        # ↑パスワードの設定は必須
        permission = Permission.objects.get(codename='add_judgement')
        user.user_permissions.add(permission)
        c = Client()
        result = c.login(username="judger",password="hoge")
        response = c.get(reverse('oogiridojo:judgement',kwargs={'pk':odai.id}))
        self.assertEquals(response.status_code,200)

    def test_show_answer_when_not_judged(self):
        odai = Odai.objects.create(odai_text="ジャッジなし")
        answer = Answer.objects.create(answer_text="あご", odai_id = odai.id)
        user = User.objects.create_user("judger", password="hoge")
        permission = Permission.objects.get(codename='add_judgement')
        user.user_permissions.add(permission)
        c = Client()
        c.login(username="judger", password="hoge")
        response = c.get(reverse('oogiridojo:judgement',kwargs={'pk':odai.id}))
        self.assertEquals(response.status_code,200)
        self.assertContains(response,"あご")
        self.assertContains(response, "judgement_form")
        # formが表示されることを、formのclassの名前でチェックしてます。

    def test_not_show_answer_when_judged(self):
        odai = Odai.objects.create(odai_text="ジャッジあり2")
        answer = Answer.objects.create(answer_text="あご", odai_id = odai.id)
        judgement = Judgement.objects.create(judgement_score=1, judgement_text="いいね", answer_id=answer.id)
        user = User.objects.create_user("judger", password="hoge")
        permission = Permission.objects.get(codename='add_judgement')
        user.user_permissions.add(permission)
        c = Client()
        c.login(username="judger", password="hoge")
        response = c.get(reverse('oogiridojo:judgement',kwargs={'pk':odai.id}))
        self.assertEquals(response.status_code,200)
        self.assertNotContains(response,"あご")
        self.assertNotContains(response,"1点。")
        self.assertNotContains(response,"いいね")
        self.assertNotContains(response, "judgement_form")
        # formが表示されないことを、formのclassの名前でチェックしてます。

    def test_add_judgement_no_permission(self):
        odai = Odai.objects.create(odai_text="oda")
        answer = Answer.objects.create(answer_text="あご", odai_id = odai.id)
        response = self.client.post(reverse("oogiridojo:judgement_submit"), {'answer_id':answer.id, 'judgement_text':"だめくそ", 'judgement_score':1})
        # パーミッションがない場合はログインページに飛ばされる。
        self.assertRedirects(response, reverse('accounts:login')+"?next=/oogiridojo/judgement_submit/")

    def test_add_judgement_with_permission(self):
        odai = Odai.objects.create(odai_text="oda")
        answer = Answer.objects.create(answer_text="あご", odai_id = odai.id)
        user = User.objects.create_user("judger", password="hoge")
        permission = Permission.objects.get(codename='add_judgement')
        user.user_permissions.add(permission)
        c = Client()
        c.login(username="judger", password="hoge")
        response = c.post(reverse("oogiridojo:judgement_submit"), {'answer_id':answer.id, 'judgement_text':"だめくそ", 'judgement_score':1})
        self.assertEqual(response.json()["score"], "1")
        self.assertEqual(response.json()["text"],"だめくそ")

class AudioSessionTests(TestCase):
    def test_toggle_not_checked_at_first(self):
        response = self.client.get(reverse('oogiridojo:index'))
        self.assertContains(response,'<input type="checkbox" id="voice_toggle" formaction="/oogiridojo/voice_toggle/" >')

    def test_toggle_still_on_when_visited_again(self):
        c = Client()
        response = c.post(reverse("oogiridojo:voice_toggle"),{'voice_toggle':'true'})
        self.assertEquals(response.content,b'true')
        response2 = c.get(reverse("oogiridojo:index"))
        self.assertContains(response2,'<input type="checkbox" id="voice_toggle" formaction="/oogiridojo/voice_toggle/" checked>')
        
    def test_toggle_still_off_when_visited_again(self):
        c = Client()
        response = c.post(reverse("oogiridojo:voice_toggle"),{'voice_toggle':'false'})
        self.assertEquals(response.content,b'false')
        response2 = c.get(reverse("oogiridojo:index"))
        self.assertContains(response2,'<input type="checkbox" id="voice_toggle" formaction="/oogiridojo/voice_toggle/" >')
