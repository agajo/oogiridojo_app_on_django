from django.contrib import admin

# Register your models here.

from .models import Odai

admin.site.register(Odai)

from .models import Answer

admin.site.register(Answer)

from .models import Tsukkomi

admin.site.register(Tsukkomi)
