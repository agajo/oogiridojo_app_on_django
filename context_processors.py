from .models import Odai

def common(request):
    context = {
        "odais": Odai.objects.all().order_by("-id"),
        "voice_toggle": voice_toggle(request)
    }
    return context

def voice_toggle(request):
    if 'voice_toggle' in request.session:
        return request.session['voice_toggle']=='true'
    else:
        return False
