from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from .models import CategoryWrite
from django.core.paginator import Paginator
from django.urls import reverse
from django.forms import ModelForm
# Create your views here.

def helo(request):
    # return HttpResponse('heeeeee!')
    return render(request, 'index.html', {})

@require_http_methods(['POST',])
def login(request):
    return JsonResponse({'status':0})


def mgr(request):
    return render(request, 'mgr.html', {})


def user_mgr(request):
    # page = request.GET.get('page', '0')
    pass


def register(request):
    pass


def category_mgr(request):
    category_writes = CategoryWrite.objects.all()
    category_writes = Paginator(category_writes, 10).page(1)
    return render(request, 'category_mgr.html', {'datas': category_writes})


def category_write_del(request, id=''):
    if id:
        id = int(id)
        CategoryWrite.objects.get(id=id).delete()
    return HttpResponseRedirect(reverse('category_mgr'))


class CategoryWriteForm(ModelForm):
    class Meta:
        model = CategoryWrite
        fields = ['name',]


def category_write_add(request):
    form = CategoryWriteForm(request.POST)
    if form.is_valid():
        form.save()
    return HttpResponseRedirect(reverse('category_mgr'))
