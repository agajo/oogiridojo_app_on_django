from django.contrib import admin

# Register your models here.

from .models import Odai
admin.site.register(Odai)

from .models import Answer
admin.site.register(Answer)

from .models import Tsukkomi
admin.site.register(Tsukkomi)

from .models import Judgement
admin.site.register(Judgement)

from django.contrib.sessions.models import Session
admin.site.register(Session)

from .models import Monkasei
admin.site.register(Monkasei)

from .models import Article
admin.site.register(Article)

from .models import Practice
admin.site.register(Practice)
