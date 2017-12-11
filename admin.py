from django.contrib import admin
from .models import Odai, Answer, Tsukkomi, Judgement, Monkasei, Article, Practice
from django.contrib.sessions.models import Session

# Register your models here.

admin.site.register(Odai)

class AnswerAdmin(admin.ModelAdmin):
    list_display = ['answer_text','monkasei']

admin.site.register(Answer, AnswerAdmin)
admin.site.register(Tsukkomi)
admin.site.register(Judgement)
admin.site.register(Session)

class MonkaseiAdmin(admin.ModelAdmin):
    list_display = ['name','ningenryoku']

admin.site.register(Monkasei, MonkaseiAdmin)
admin.site.register(Article)
admin.site.register(Practice)
