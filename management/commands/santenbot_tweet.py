from django.core.management.base import BaseCommand, CommandError
from PIL import Image
from .santenbot import make_santen_picture
import random
from django.db.models import Count
from ...models import Odai, Answer, Judgement
import tweepy
from .twitter_secrets import consumer_key, consumer_secret, access_token, access_token_secret

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

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    text = judgement.answer.odai.odai_text + " http://oka-ryunoske.work/oogiridojo/odai/" + str(judgement.answer.odai.id) + "/#answer_id_" + str(judgement.answer.id)
    api.update_with_media("./santenbot_img.png", status=text)
