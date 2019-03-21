from django.shortcuts import render, render_to_response
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from .models import CategoryWrite, CategoryContent, User, UserInfo
from django.core.paginator import Paginator
from django.urls import reverse
from django.forms import ModelForm
import hashlib, json
# Create your views here.

def helo(request):
    # return HttpResponse('heeeeee!')
    return render(request, 'index.html', {})

def make_passwd(psw, salt):
    psw = ''.join((psw, salt))
    psw = psw.encode('utf-8')
    ret = hashlib.sha512(psw).hexdigest()
    return ret


@require_http_methods(['POST',])
def login(request):
    name = request.POST.get('name','').strip()
    password = request.POST.get('password','').strip()
    if name and password:
        u = User.objects.filter(name=name).first()
        if u:
            if u.passwd == make_passwd(password, u.name):
                resp = JsonResponse({'status':0})
                resp.set_cookie('userid', u.id)
                return resp
    return JsonResponse({'status':1})


def mgr(request):
    return render(request, 'mgr.html', {})


def register(request):
    if request.method == 'GET':
        return render(request, 'reg.html', {'info':''})
    else:
        info = ''
        params = {}
        keys = ('name', 'password1', 'password2', 'email')
        for key in keys:
            params[key] = request.POST.get(key, '').strip()
        print(params)
        if len(params) != len(keys):
            info = '你输入的信息不全！'
        elif params['password1'] != params['password2']:
            info = '密码不匹配!'
        else:
            un = User.objects.filter(name=params['name'])
            ue = User.objects.filter(email=params['email'])
            if un or ue:
                info = '用户名或邮箱已被注册！'
            else:
                passwd = make_passwd(params['password1'],params['name'])
                u = User(name=params['name'], email=params['email'],
                     passwd=passwd)
                u.save()
        if info:
            resp = render(request, 'reg.html', {'info':info})
            return  resp
        else:
            resp = HttpResponseRedirect(reverse('helo'))
            resp.set_cookie('userid', u.id)
            return  resp


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
        return render(request, 'user_mgr.html', {'users':users})
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
                reason = request.POST.get('reason','')
                UserInfo(content=reason, user=u).save()
                u.save()
            elif operation == 2:
                u = User.objects.get(id=int(uid))
                if u:
                    u.status = 2
                    u.save()
        return HttpResponseRedirect(reverse('user_mgr'))


