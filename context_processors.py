from .models import Odai

def common(request):
    context = {
        "odais": Odai.objects.all().order_by("-id"),
    }
    return context
