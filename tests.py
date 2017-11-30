from django.test import TestCase, Client
from .models import Odai, Answer, Tsukkomi, Judgement, Monkasei, Article, Practice
from django.urls import reverse
from django.contrib.auth.models import User, Permission

# Create your tests here.

class OdaiModelTests(TestCase):
    def test_answer_list_order(self):
        odai = Odai.objects.create(id = 1, odai_text="test_answer_list_order")
        monkasei = Monkasei.objects.create(id=1, name="mon1")
        ans1 = Answer.objects.create(answer_text="ans1", odai_id=1, modified_date="2017-01-01T01:01:03+09:00", monkasei_id=1)
        ans2 = Answer.objects.create(answer_text="ans2", odai_id=1, modified_date="2017-01-01T01:01:03+09:00", monkasei_id=1)
        ans3 = Answer.objects.create(answer_text="ans3", odai_id=1, modified_date="2017-01-01T01:01:03+09:00", monkasei_id=1)
        ans2.answer_text="ans2_2"
        #ポスグレだと、この操作をすることで、取り出される順番が変わることがある。それが発生していないかチェックしている。
        ans2.save()
        self.assertQuerysetEqual(odai.answer_list(),['<Answer: ans3>', '<Answer: ans2_2>','<Answer: ans1>'])
        #最新の投稿を先に表示します。

    def test_answer_list_order_with_modified_date(self):
        odai = Odai.objects.create(id = 1, odai_text="answer_list_order_with_modified_date")
        monkasei = Monkasei.objects.create(id=1, name="mon1")
        ans1 = Answer.objects.create(answer_text="ans1", odai_id=1, modified_date="2017-01-01T01:01:03+09:00", monkasei_id=1)
        ans2 = Answer.objects.create(answer_text="ans2", odai_id=1, modified_date="2017-01-01T01:01:04+09:00", monkasei_id=1)
        ans3 = Answer.objects.create(answer_text="ans3", odai_id=1, modified_date="2017-01-01T01:01:03+09:00", monkasei_id=1)
        self.assertQuerysetEqual(odai.answer_list(),['<Answer: ans3>', '<Answer: ans2>','<Answer: ans1>'])
        #modified dateは無視して新しい順に。

    def test_number_one_answer(self):
        odai = Odai.objects.create(id=1, odai_text="test_number_one_answer")
        monkasei = Monkasei.objects.create(id=1, name="mon1")
        ans1 = Answer.objects.create(answer_text="ans1", odai_id=1, free_vote_score=1, monkasei_id=1)
        ans2 = Answer.objects.create(answer_text="ans2", odai_id=1, free_vote_score=300, monkasei_id=1)
        ans3 = Answer.objects.create(answer_text="ans3", odai_id=1, free_vote_score=50, monkasei_id=1)
        anslist = odai.answer_list()
        self.assertFalse(anslist[0].is_number_one)
        self.assertTrue(anslist[1].is_number_one)
        self.assertFalse(anslist[2].is_number_one)

class IndexViewTests(TestCase):
    def test_only_one_newest_odai_shown(self):
        odai1 = Odai.objects.create(odai_text="test_odai_order1")
        odai2 = Odai.objects.create(odai_text="test_odai_order2")
        response = self.client.get(reverse('oogiridojo:index'))
        self.assertContains(response,"test_odai_order2</h1>")
        self.assertNotContains(response,"test_odai_order1</h1>")
        #お題一覧にどうせ両方含まれるので、コンテンツ内の<h1>の方でチェック
        self.assertContains(response,"<title>岡竜之介の大喜利道場</title>")

class OdaiViewAnswersTests(TestCase):
    def test_no_answers(self):
        odai = Odai.objects.create(odai_text="odaoda")
        response = self.client.get(reverse('oogiridojo:odai',kwargs={'pk':odai.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "回答がありません")

    def test_an_answer(self):
        odai = Odai.objects.create(odai_text="oda")
        monkasei = Monkasei.objects.create(id=1, name="mon1")
        Answer.objects.create(answer_text="ほげほげ", odai_id = odai.id, monkasei_id=1)
        response = self.client.get(reverse('oogiridojo:odai',kwargs={'pk':odai.id}))
        self.assertContains(response,"ほげほげ")

    def test_an_answer_with_free_vote_score(self):
        odai = Odai.objects.create(odai_text="oda")
        monkasei = Monkasei.objects.create(id=1, name="mon1")
        Answer.objects.create(answer_text="ふが", free_vote_score=1, odai_id = odai.id, monkasei_id=1)
        response = self.client.get(reverse('oogiridojo:odai',kwargs={'pk':odai.id}))
        self.assertContains(response,'<strong class="free_vote_score">1</strong>')

    def test_an_answer_with_tsukkomi(self):
        odai = Odai.objects.create(odai_text="oda")
        monkasei = Monkasei.objects.create(id=1, name="mon1")
        answer = Answer.objects.create(answer_text="ふが", odai_id = odai.id, monkasei_id=1)
        tsukkomi = Tsukkomi.objects.create(tsukkomi_text="つっこみます", answer_id=answer.id)
        response = self.client.get(reverse('oogiridojo:odai',kwargs={'pk':odai.id}))
        self.assertContains(response,"つっこみます")

    def test_free_vote_score_increment(self):
        odai = Odai.objects.create(odai_text="oda")
        monkasei = Monkasei.objects.create(id=1, name="mon1")
        answer = Answer.objects.create(answer_text="ふが", free_vote_score=1, odai_id = odai.id, monkasei_id=1)
        response = self.client.post(reverse("oogiridojo:free_vote"), {'free_vote_button':answer.id})
        self.assertEqual(response.json()["newscore"], 2)

    def test_tsukkomi_submit(self):
        odai = Odai.objects.create(odai_text="oda")
        monkasei = Monkasei.objects.create(id=1, name="mon1")
        answer = Answer.objects.create(answer_text="ふが", free_vote_score=1, odai_id = odai.id, monkasei_id=1)
        response = self.client.post(reverse("oogiridojo:tsukkomi_submit"), {'answer_id':answer.id, 'tsukkomi_text':"つっこみ"})
        self.assertEqual(response.json()["return_tsukkomi"],"つっこみ")

    def test_tsukkomi_submit_and_modify_answer_date(self):
        odai = Odai.objects.create(odai_text="oda")
        monkasei = Monkasei.objects.create(id=1, name="mon1")
        answer1 = Answer.objects.create(answer_text="ans1", odai_id = odai.id, modified_date="2017-01-01T01:01:01+09:00", monkasei_id=1)
        answer2 = Answer.objects.create(answer_text="ans2", odai_id = odai.id, modified_date="2017-01-01T01:01:01+09:00", monkasei_id=1)
        answer3 = Answer.objects.create(answer_text="ans3", odai_id = odai.id, modified_date="2017-01-01T01:01:01+09:00", monkasei_id=1)
        response = self.client.post(reverse("oogiridojo:tsukkomi_submit"), {'answer_id':answer2.id, 'tsukkomi_text':"つっこみ"})
        self.assertQuerysetEqual(odai.answer_list(),['<Answer: ans3>', '<Answer: ans2>','<Answer: ans1>'])

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
        monkasei = Monkasei.objects.create(id=1, name="mon1")
        answer = Answer.objects.create(answer_text="あご", odai_id = odai.id, monkasei_id=1)
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
        self.assertEqual(response.status_code,200)

    def test_show_answer_when_not_judged(self):
        odai = Odai.objects.create(odai_text="ジャッジなし")
        monkasei = Monkasei.objects.create(id=1, name="mon1")
        answer = Answer.objects.create(answer_text="あご", odai_id = odai.id, monkasei_id=1)
        user = User.objects.create_user("judger", password="hoge")
        permission = Permission.objects.get(codename='add_judgement')
        user.user_permissions.add(permission)
        c = Client()
        c.login(username="judger", password="hoge")
        response = c.get(reverse('oogiridojo:judgement',kwargs={'pk':odai.id}))
        self.assertEqual(response.status_code,200)
        self.assertContains(response,"あご")
        self.assertContains(response, "judgement_form")
        # formが表示されることを、formのclassの名前でチェックしてます。

    def test_not_show_answer_when_judged(self):
        odai = Odai.objects.create(odai_text="ジャッジあり2")
        monkasei = Monkasei.objects.create(id=1, name="mon1")
        answer = Answer.objects.create(answer_text="あご", odai_id = odai.id, monkasei_id=1)
        judgement = Judgement.objects.create(judgement_score=1, judgement_text="いいね", answer_id=answer.id)
        user = User.objects.create_user("judger", password="hoge")
        permission = Permission.objects.get(codename='add_judgement')
        user.user_permissions.add(permission)
        c = Client()
        c.login(username="judger", password="hoge")
        response = c.get(reverse('oogiridojo:judgement',kwargs={'pk':odai.id}))
        self.assertEqual(response.status_code,200)
        self.assertNotContains(response,"あご")
        self.assertNotContains(response,"1点。")
        self.assertNotContains(response,"いいね")
        self.assertNotContains(response, "judgement_form")
        # formが表示されないことを、formのclassの名前でチェックしてます。

    def test_add_judgement_no_permission(self):
        odai = Odai.objects.create(odai_text="oda")
        monkasei = Monkasei.objects.create(id=1, name="mon1")
        answer = Answer.objects.create(answer_text="あご", odai_id = odai.id, monkasei_id=1)
        response = self.client.post(reverse("oogiridojo:judgement_submit"), {'answer_id':answer.id, 'judgement_text':"だめくそ", 'judgement_score':1})
        # パーミッションがない場合はログインページに飛ばされる。
        self.assertRedirects(response, reverse('accounts:login')+"?next=/oogiridojo/judgement_submit/")

    def test_add_judgement_with_permission(self):
        odai = Odai.objects.create(odai_text="oda")
        monkasei = Monkasei.objects.create(id=1, name="mon1")
        answer = Answer.objects.create(answer_text="あご", odai_id = odai.id, monkasei_id=1)
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
        self.assertEqual(response.content,b'true')
        response2 = c.get(reverse("oogiridojo:index"))
        self.assertContains(response2,'<input type="checkbox" id="voice_toggle" formaction="/oogiridojo/voice_toggle/" checked>')
        
    def test_toggle_still_off_when_visited_again(self):
        c = Client()
        response = c.post(reverse("oogiridojo:voice_toggle"),{'voice_toggle':'false'})
        self.assertEqual(response.content,b'false')
        response2 = c.get(reverse("oogiridojo:index"))
        self.assertContains(response2,'<input type="checkbox" id="voice_toggle" formaction="/oogiridojo/voice_toggle/" >')

class JudgerViewTests(TestCase):
    def test_no_permission(self):
        response = self.client.get(reverse('oogiridojo:judger'))
        # パーミッションがない場合はログインページに飛ばされる。
        self.assertRedirects(response, reverse('accounts:login')+"?next=/oogiridojo/judger/")
        # nextパラメータが付くので注意

    def test_show_judge_ratio(self):
        odai = Odai.objects.create(odai_text="ジャッジあり2")
        monkasei = Monkasei.objects.create(id=1, name="mon1")
        answer1 = Answer.objects.create(answer_text="あご", odai_id = odai.id, monkasei_id=1)
        answer2 = Answer.objects.create(answer_text="あご", odai_id = odai.id, monkasei_id=1)
        answer3 = Answer.objects.create(answer_text="あご", odai_id = odai.id, monkasei_id=1)
        answer4 = Answer.objects.create(answer_text="あご", odai_id = odai.id, monkasei_id=1)
        answer5 = Answer.objects.create(answer_text="あご", odai_id = odai.id, monkasei_id=1)
        Judgement.objects.create(judgement_score=1, judgement_text="いいね", answer_id=answer1.id)
        Judgement.objects.create(judgement_score=2, judgement_text="いいね", answer_id=answer2.id)
        Judgement.objects.create(judgement_score=2, judgement_text="いいね", answer_id=answer3.id)
        Judgement.objects.create(judgement_score=3, judgement_text="いいね", answer_id=answer4.id)
        Judgement.objects.create(judgement_score=3, judgement_text="いいね", answer_id=answer5.id)
        user = User.objects.create_user("judger", password="hoge")
        permission = Permission.objects.get(codename='add_judgement')
        user.user_permissions.add(permission)
        c = Client()
        c.login(username="judger", password="hoge")
        response = c.get(reverse('oogiridojo:judger'))
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['ratio1'],20.0)
        self.assertEqual(response.context['ratio2'],40.0)
        self.assertEqual(response.context['ratio3'],40.0)

class YoiRankingViewTests(TestCase):
    def test_ranking_context(self):
        odai = Odai.objects.create(odai_text="良いランキングのテスト")
        monkasei = Monkasei.objects.create(id=1, name="mon1")
        answer1 = Answer.objects.create(answer_text="uu", free_vote_score=1, odai_id = odai.id, monkasei_id=1)
        answer2 = Answer.objects.create(answer_text="iiii", free_vote_score=2, odai_id = odai.id, monkasei_id=1)
        response = self.client.get(reverse('oogiridojo:yoi_ranking'))
        self.assertQuerysetEqual(response.context['answer_list'],['<Answer: iiii>', '<Answer: uu>'])

    def test_ranking_not_show_old_answer(self):
        odai = Odai.objects.create(odai_text="良いランキングのテスト")
        monkasei = Monkasei.objects.create(id=1, name="mon1")
        answer1 = Answer.objects.create(answer_text="uu", free_vote_score=5, odai_id = odai.id, creation_date="2000-10-10T11:11:11+09:00", monkasei_id=1)
        answer2 = Answer.objects.create(answer_text="iiii", free_vote_score=2, odai_id = odai.id, monkasei_id=1)
        response = self.client.get(reverse('oogiridojo:yoi_ranking'))
        self.assertQuerysetEqual(response.context['answer_list'],['<Answer: iiii>'])

class GreatAnswersViewTests(TestCase):
    def test_ranking_context(self):
        odai = Odai.objects.create(odai_text="great answer test")
        monkasei = Monkasei.objects.create(id=1, name="mon1")
        answer1 = Answer.objects.create(answer_text="uu", odai_id = odai.id, monkasei_id=1)
        answer2 = Answer.objects.create(answer_text="ww", odai_id = odai.id, monkasei_id=1)
        answer3 = Answer.objects.create(answer_text="ii", odai_id = odai.id, monkasei_id=1)
        answer4 = Answer.objects.create(answer_text="iiiiii", odai_id = odai.id, monkasei_id=1)
        Judgement.objects.create(judgement_score=3, judgement_text="uuu", answer_id=answer1.id)
        Judgement.objects.create(judgement_score=1, judgement_text="www", answer_id=answer2.id)
        Judgement.objects.create(judgement_score=3, judgement_text="iii", answer_id=answer3.id)
        Judgement.objects.create(judgement_score=2, judgement_text="gagagaiii", answer_id=answer4.id)
        response = self.client.get(reverse('oogiridojo:great_answers'))
        self.assertQuerysetEqual(response.context['judgement_list'],['<Judgement: iii>', '<Judgement: uuu>'])
        #新しい順に出ること、ランク3だけが出ること、をチェックしてます。

class MypageViewTests(TestCase):
    def test_mypage_answers(self):
        odai = Odai.objects.create(odai_text="mypage view answers")
        c1 = Client()
        c2 = Client()
        c1.post(reverse("oogiridojo:answer_submit"), {'odai_id':odai.id, 'answer_text':"aaaaaa"})
        c2.post(reverse("oogiridojo:answer_submit"), {'odai_id':odai.id, 'answer_text':"iiiiii"})
        c1.post(reverse("oogiridojo:answer_submit"), {'odai_id':odai.id, 'answer_text':"uuuuuu"})
        c2.post(reverse("oogiridojo:answer_submit"), {'odai_id':odai.id, 'answer_text':"eeeeee"})
        response = c1.get(reverse('oogiridojo:mypage'))
        self.assertContains(response,"aaaaaa")
        self.assertContains(response,"uuuuuu")
        self.assertNotContains(response,"iiiiii")
        self.assertNotContains(response,"eeeeee")
        #該当する本人の回答だけ表示されるかテスト

    def test_mypage_name(self):
        odai = Odai.objects.create(odai_text="mypage view answers")
        c1 = Client()
        c1.post(reverse("oogiridojo:answer_submit"), {'odai_id':odai.id, 'answer_text':"aaaaaa"})
        #answerを投稿することで、門下生としてのデータが作られる
        monkasei = Monkasei.objects.get(pk=1)
        response = c1.get(reverse('oogiridojo:mypage'))
        self.assertContains(response,monkasei.name)

    def test_mypage_score(self):
        odai = Odai.objects.create(odai_text="mypage view answers")
        c1 = Client()
        c1.post(reverse("oogiridojo:answer_submit"), {'odai_id':odai.id, 'answer_text':"aaaaaa"})
        for i in range(143):
            self.client.post(reverse("oogiridojo:free_vote"), {'free_vote_button':1})#作ったanswerのidは1でしょう
        response = c1.get(reverse('oogiridojo:mypage'))
        self.assertContains(response,"143")

    def test_mypage_not_calculate_old_answers(self):
        odai = Odai.objects.create(odai_text="mypage view answers")
        c1 = Client()
        c1.post(reverse("oogiridojo:answer_submit"), {'odai_id':odai.id, 'answer_text':"aaaaaa"})
        monkasei = Monkasei.objects.get(pk=1)
        answer1 = Answer.objects.create(answer_text="uu", odai_id = odai.id, monkasei_id=1, free_vote_score=136)
        answer2 = Answer.objects.create(answer_text="ww", odai_id = odai.id, monkasei_id=1, free_vote_score=123, creation_date="2010-10-10T03:03:03+09:00")
        response = c1.get(reverse('oogiridojo:mypage'))
        self.assertContains(response,"最近の良い数は136です。")
        self.assertContains(response,"123")#回答自体を表示する方には古い奴も出る

#↓↓↓↓ここから、大喜利の「型」がらみのテストです。本当は分割したいけどやり方がわからんので。
#いつかわかったら分割しておいて。2017-11-14

class ArticleModelTests(TestCase):
    def test_next_prev(self):
        article1 = Article.objects.create(title="aaaaa", content="bbbbb", practice_odai="ccccc")
        article2 = Article.objects.create(title="aaaa2", content="bbbb2", practice_odai="cccc2")
        self.assertFalse(article1.get_prev())
        self.assertFalse(article2.get_next())
        self.assertEqual(article1.get_next().title,"aaaa2")
        self.assertEqual(article2.get_prev().title,"aaaaa")

class ArticleListViewTests(TestCase):
    def test_article_list_context(self):
        article1 = Article.objects.create(title="aaaaa", content="bbbbb", practice_odai="ccccc")
        article2 = Article.objects.create(title="aaaa2", content="bbbb2", practice_odai="cccc2")
        response = self.client.get(reverse('oogiridojo:article_list'))
        self.assertQuerysetEqual(response.context['article_list'],['<Article: aaaaa>', '<Article: aaaa2>'])

class ArticleViewTests(TestCase):
    def test_article_content(self):
        article = Article.objects.create(title="aaaaa", content="bbbbb", practice_odai="ccccc")
        response = self.client.get(reverse('oogiridojo:article', kwargs={'pk':article.id}))
        self.assertContains(response,"aaaaa")
        self.assertContains(response,"bbbbb")
        self.assertContains(response,"ccccc")

    def test_article_practice_answers(self):
        article = Article.objects.create(title="aaaaa", content="bbbbb", practice_odai="ccccc")
        practice = Practice.objects.create(answer_text="ddddd", article_id=article.id)
        response = self.client.get(reverse('oogiridojo:article', kwargs={'pk':article.id}))
        self.assertContains(response,"ddddd")

class PracticeSubmitViewTests(TestCase):
    def test_practice_submit(self):
        article = Article.objects.create(title="aaaaa", content="bbbbb", practice_odai="ccccc")
        response = self.client.post(reverse("oogiridojo:practice_submit"), {'article_id':article.id, 'practice_text':"つっこみ"})
        self.assertEqual(response.json()["return_practice"],"つっこみ")
#「型」がらみのテストここまで↑↑↑↑

class MonkaseiYoiRankingViewTests(TestCase):
    def test_monkasei_order(self):
        odai = Odai.objects.create(odai_text="mypage view answers")
        c1 = Client()
        c2 = Client()
        c1.post(reverse("oogiridojo:answer_submit"), {'odai_id':odai.id, 'answer_text':"aaaaaa"})
        c2.post(reverse("oogiridojo:answer_submit"), {'odai_id':odai.id, 'answer_text':"iiiiii"})
        c1.post(reverse("oogiridojo:answer_submit"), {'odai_id':odai.id, 'answer_text':"uuuuuu"})
        c2.post(reverse("oogiridojo:answer_submit"), {'odai_id':odai.id, 'answer_text':"eeeeee"})
        for i in range(43):
            self.client.post(reverse("oogiridojo:free_vote"), {'free_vote_button':1})#作ったanswerのidは一つ目は1でしょう
        for i in range(433):
            self.client.post(reverse("oogiridojo:free_vote"), {'free_vote_button':2})
        response = c1.get(reverse('oogiridojo:monkasei_yoi_ranking'))
        monkasei1 = Monkasei.objects.get(pk=1)
        monkasei2 = Monkasei.objects.get(pk=2)
        self.assertQuerysetEqual(response.context['monkasei_list'],['<Monkasei: '+monkasei2.name+'>', '<Monkasei: '+monkasei1.name+'>'])
        self.assertContains(response,"40")
        self.assertContains(response,"430")

    def test_not_calculate_old_answer(self):
        odai = Odai.objects.create(odai_text="mypage view answers")
        c1 = Client()
        c2 = Client()
        c1.post(reverse("oogiridojo:answer_submit"), {'odai_id':odai.id, 'answer_text':"aaaaaa"})
        c2.post(reverse("oogiridojo:answer_submit"), {'odai_id':odai.id, 'answer_text':"iiiiii"})
        answer1 = Answer.objects.create(answer_text="uu", odai_id = odai.id, monkasei_id=1, free_vote_score=106)
        answer2 = Answer.objects.create(answer_text="ww", odai_id = odai.id, monkasei_id=1, free_vote_score=123, creation_date="2010-10-10T03:03:03+09:00")
        answer3 = Answer.objects.create(answer_text="uu", odai_id = odai.id, monkasei_id=2, free_vote_score=137)
        response = c1.get(reverse('oogiridojo:monkasei_yoi_ranking'))
        monkasei1 = Monkasei.objects.get(pk=1)
        monkasei2 = Monkasei.objects.get(pk=2)
        self.assertQuerysetEqual(response.context['monkasei_list'],['<Monkasei: '+monkasei2.name+'>', '<Monkasei: '+monkasei1.name+'>'])
        self.assertContains(response,"110")
        self.assertContains(response,"140")
