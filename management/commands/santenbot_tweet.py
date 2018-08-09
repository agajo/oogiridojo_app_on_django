from django.core.management.base import BaseCommand, CommandError
from PIL import Image
from .santenbot import make_santen_picture
import random
from django.db.models import Count
from ...models import Odai, Answer, Judgement

class Command(BaseCommand):
  help = "makes Santenbot tweet"

  def handle(self, *args, **options):
    count = Judgement.objects.filter(judgement_score__exact = 3).aggregate(count=Count('id'))["count"]
    i = random.choice(range(0,count))
    judgement = Judgement.objects.filter(judgement_score__exact = 3).order_by('id')[i]
    if(judgement.answer.img_datauri):
      img_uri = judgement.answer.img_datauri
    else:
      img_uri = ""
    image = make_santen_picture(judgement.answer.odai.odai_text, judgement.answer.answer_text, img_uri) 
    image.save("./santenbot_img.png")
