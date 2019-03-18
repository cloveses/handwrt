from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods

# Create your views here.

def helo(request):
    # return HttpResponse('heeeeee!')
    return render(request, 'index.html', {})

@require_http_methods(['POST',])
def login(request):
    return JsonResponse({'status':0})