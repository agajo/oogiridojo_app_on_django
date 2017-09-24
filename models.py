from django.db import models
from django.utils import timezone

# Create your models here.

class Odai(models.Model):
    odai_text = models.CharField(max_length=100)
    example_text = models.CharField(max_length = 50)
    creation_date = models.DateTimeField('date created', default=timezone.now)
    def __str__(self):
        return self.odai_text

class Answer(models.Model):
    odai = models.ForeignKey(Odai, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=200)
    creation_date = models.DateTimeField('date created', default=timezone.now)
    free_vote_score = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.answer_text
