from django.db import models
from django.utils import timezone
import datetime

# Create your models here.
from django.db.models import Max, Sum, Count

class Odai(models.Model):
    odai_text = models.CharField(max_length=100)
    example_text = models.CharField(max_length = 50)
    creation_date = models.DateTimeField('date created', default=timezone.now)
    def __str__(self):
        return self.odai_text
    def answer_list(self):
        anslist = self.answer_set.all().order_by('-id')
        # checking number one answer from here
        max_free_vote_score_dict = self.answer_set.aggregate(Max('free_vote_score'))
        for answer in anslist:
            if answer.free_vote_score == max_free_vote_score_dict["free_vote_score__max"]:
                answer.is_number_one = True
            else:
                answer.is_number_one = False
        return anslist

class Monkasei(models.Model):
    name = models.CharField(max_length=30)
    ningenryoku = models.PositiveIntegerField(default=20)
    creation_date = models.DateTimeField('date created', default=timezone.now)
    def __str__(self):
        return self.name
    def recent_free_vote_score(self):
        return self.answer_set.filter(creation_date__gte = timezone.now() - datetime.timedelta(days=14)).aggregate(score=Sum('free_vote_score'))['score']
        #adminとmypageで使用。ランキング表示にも使いたかったけど、このpythonサイドの情報を元にしたSQLは発行できない。
        #同じ理由で、adminでもこの点数をもとに並び替えはできない。
    def recent_great_answer_count(self):
        return self.answer_set.filter(judgement__creation_date__gte = timezone.now() - datetime.timedelta(days=14), judgement__judgement_score__exact = 3).aggregate(great_count = Count('judgement'))['great_count']

class Answer(models.Model):
    odai = models.ForeignKey(Odai, on_delete=models.CASCADE)
    monkasei = models.ForeignKey(Monkasei, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=300)
    img_datauri = models.TextField(blank=True)
    creation_date = models.DateTimeField('date created', default=timezone.now)
    modified_date = models.DateTimeField('date modified', default=timezone.now)
    free_vote_score = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.answer_text

class Tsukkomi(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    tsukkomi_text = models.CharField(max_length=200)
    creation_date = models.DateTimeField('date created', default=timezone.now)
    def __str__(self):
        return self.tsukkomi_text

class Judgement(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    judgement_text = models.CharField(max_length=200)
    judgement_score = models.PositiveIntegerField(default=0)
    creation_date = models.DateTimeField('date created', default=timezone.now)
    def __str__(self):
        return self.judgement_text

class Article(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    practice_odai = models.CharField(max_length=100)
    creation_date = models.DateTimeField('date created', default=timezone.now)
    def __str__(self):
        return self.title
    def get_next(self):
        try:
            next = Article.objects.get(id=self.id+1)
            return next
        except Article.DoesNotExist:
            return False
    def get_prev(self):
        try:
            prev = Article.objects.get(id=self.id-1)
            return prev
        except Article.DoesNotExist:
            return False

class Practice(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=300)
    creation_date = models.DateTimeField('date created', default=timezone.now)
    def __str__(self):
        return self.answer_text
