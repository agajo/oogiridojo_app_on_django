from django.db import models
from django.utils import timezone

# Create your models here.

class Answer(models.Model):
    answer_text = models.CharField(max_length=200)
    creation_date = models.DateTimeField('date created', default=timezone.now)
    free_vote_score = models.PositiveIntegerField(default=0)
