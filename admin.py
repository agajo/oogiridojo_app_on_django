from django.contrib import admin
from .models import Odai, Answer, Tsukkomi, Judgement, Monkasei, Article, Practice
from django.contrib.sessions.models import Session

# Register your models here.

admin.site.register(Odai)

class AnswerAdmin(admin.ModelAdmin):
    list_display = ['answer_text','monkasei','client_ip']

admin.site.register(Answer, AnswerAdmin)
admin.site.register(Tsukkomi)
admin.site.register(Judgement)
admin.site.register(Session)

class MonkaseiAdmin(admin.ModelAdmin):
    list_display = ['name','ningenryoku','recent_great_answer_count','recent_free_vote_score']

admin.site.register(Monkasei, MonkaseiAdmin)
admin.site.register(Article)
admin.site.register(Practice)
