from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from .models import CategoryWrite, CategoryContent, User, UserInfo
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
    category_contents = CategoryContent.objects.all()
    category_contents = Paginator(category_contents, 10).page(1)
    parent_contents = CategoryContent.objects.filter(parent__isnull=True)
    return render(request, 'category_mgr.html',
                  {'datas': category_writes, 'data_cs':category_contents,
                   'parent_contents':parent_contents})


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

def category_content_add(request):
    name = request.POST.get('name', '')
    pid = request.POST.get('parent', '')
    if name and pid and pid.isdigit():
        pid = int(pid)
        p = CategoryContent.objects.get(id=pid)
        if p:
            CategoryContent(name=name, parent=p).save()
    return HttpResponseRedirect(reverse('category_mgr'))


def user_mgr(request):
    if request.method == 'GET':
        users = User.objects.all()
        users = Paginator(users, 10).page(1)
        return render(request, 'usermgr.html', {'users':users})
    elif request.method == 'POST':
        operation = request.POST.get('operation', '')
        uid = request.POST.get('id', '')
        if operation and uid and operation.isdigit() and uid.isdigit():
            if operation == 0:
                User.objects.get(id=int(uid)).delete()
            elif operation == 1:
                u = User.objects.get(id=int(uid))
                if u:
                    u.status = 1


