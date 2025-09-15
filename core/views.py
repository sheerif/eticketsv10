from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.utils.timezone import now

@ensure_csrf_cookie
def index(request):
    return render(request, "home.html")

def health(request):
    return JsonResponse({"status": "ok", "time": now().isoformat()})
