from django.shortcuts import render, render_to_response
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpResponseNotFound
from django.views.decorators.http import require_http_methods
from .models import CategoryWrite, CategoryContent, User, UserInfo, Union, UnionInfo, HandWrite, Comment
from django.core.paginator import Paginator
from django.urls import reverse
from django.forms import ModelForm
import hashlib, json, os
import datetime
from django.utils.timezone import utc
# Create your views here.
SUPER_PERM = [0,]
UNION_PERM = [1,]
SUPER_UNION = [0, 1]
ORDINARY_PERM = [2,]
ALL_PERM = [0,1,2]
PAGE_ITEMS = 2

def make_passwd(psw, salt):
    psw = ''.join((psw, salt))
    psw = psw.encode('utf-8')
    ret = hashlib.sha512(psw).hexdigest()
    return ret


def login_error(request, utypes=None):
    u = request.COOKIES.get('userid','').strip()
    utype = request.COOKIES.get('utype','').strip()
    if not u or not utype:
        return True
    if utypes and utype and int(utype) not in utypes:
        return True

def get_category_content_menus():
    menus = {}
    parent_contents = CategoryContent.objects.filter(parent=None).all()
    for parent_content in parent_contents:
        children = CategoryContent.objects.filter(parent=parent_content).all()
        children_menus = [(child.id,child.name) for child in children]
        # print(children_menus)
        menus[(parent_content.id, parent_content.name)] = children_menus
    return menus


def helo(request):
    # return HttpResponse('heeeeee!')
    username = request.COOKIES.get('username','').strip()
    utype = request.COOKIES.get('utype','').strip()
    cws = CategoryWrite.objects.all()
    return render(request, 'index.html', 
        {'cws':cws, 'utype':utype, 'username':username,'menus':get_category_content_menus()})

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
                resp.set_cookie('username', u.name)
                resp.set_cookie('utype', u.permission)
                return resp
    return JsonResponse({'status':1})


# def mgr(request):
#     permission = request.COOKIES.get('utype','')
#     if permission == '0':
#         return render(request, 'mgr.html', {})
#     else:
#         return HttpResponseNotFound('<h1>Page not found</h1>')


#超级管理员管理页面
def mgr(request):
    if login_error(request, SUPER_PERM):
        return HttpResponseRedirect(reverse('helo'))
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
            resp.set_cookie('utype', u.permission)
            resp.set_cookie('username',u.name)
            return  resp

def category_mgr(request):
    if login_error(request, SUPER_PERM):
        return HttpResponseRedirect(reverse('helo'))
    category_writes = CategoryWrite.objects.all()
    # category_writes = Paginator(category_writes, PAGE_ITEMS).page(1)
    category_contents = CategoryContent.objects.all()
    # category_contents = Paginator(category_contents, PAGE_ITEMS).page(1)
    parent_contents = CategoryContent.objects.filter(parent__isnull=True)
    return render(request, 'category_mgr.html',
                  {'datas': category_writes, 'data_cs':category_contents,
                   'parent_contents':parent_contents})


def category_write_del(request, id=''):
    if login_error(request, SUPER_PERM):
        return HttpResponseRedirect(reverse('helo'))
    if id:
        id = int(id)
        CategoryWrite.objects.get(id=id).delete()
    return HttpResponseRedirect(reverse('category_mgr'))


class CategoryWriteForm(ModelForm):
    class Meta:
        model = CategoryWrite
        fields = ['name',]


def category_write_add(request):
    if login_error(request, SUPER_PERM):
        return HttpResponseRedirect(reverse('helo'))
    form = CategoryWriteForm(request.POST)
    if form.is_valid():
        form.save()
    return HttpResponseRedirect(reverse('category_mgr'))


def category_content_add(request):
    if login_error(request, SUPER_PERM):
        return HttpResponseRedirect(reverse('helo'))
    name = request.POST.get('name', '')
    pid = request.POST.get('parent', '')
    if not pid:
        pid = '0'
    print(name, pid)
    if name and pid and pid.isdigit():
        pid = int(pid)
        if pid == 0:
            CategoryContent(name=name).save()
        else:
            p = CategoryContent.objects.get(id=pid)
            if p:
                CategoryContent(name=name, parent=p).save()
    return HttpResponseRedirect(reverse('category_mgr'))

def category_content_del(request, id=''):
    if login_error(request, SUPER_PERM):
        return HttpResponseRedirect(reverse('helo'))
    if id:
        id = int(id)
        CategoryContent.objects.get(id=id).delete()
    return HttpResponseRedirect(reverse('category_mgr'))

def get_page(page, page_range, total_pages=5):
    page_count = len(page_range)
    if page_count <= total_pages:
        return list(page_range)
    elif page_count - page <= 5:
        return list(page_range[-5:])
    else:
        return page_range[page: page + 5]


def user_mgr(request, page=1):
    if login_error(request, SUPER_UNION):
        print('login err')
        return HttpResponseRedirect(reverse('helo'))
    if request.method == 'GET':
        u = request.COOKIES.get('userid','').strip()
        u = User.objects.get(id=int(u))
        if u.permission == 0:
            users = User.objects.all()
        else:
            union = Union.objects.get(owner=u)
            users = union.users.all()
        users = Paginator(users, PAGE_ITEMS)
        page_nums = get_page(page, users.page_range)
        return render(request, 'user_mgr.html', {'users':users.page(page),'page': page, 'page_nums':page_nums, 'num_pages': users.num_pages})
    elif request.method == 'POST':
        operation = request.POST.get('operation', '')
        uid = request.POST.get('id', '')
        if operation and uid and operation.isdigit() and uid.isdigit():
            if operation == '0':
                # edit
                # User.objects.get(id=int(uid)).delete()
                u = User.objects.get(id=int(uid))
                un = u.members.all().first()
                un.users.remove(u)
                un.save()

            elif operation == '1':
                u = User.objects.get(id=int(uid))
                if u:
                    u.status = 1
                reason = request.POST.get('reason','')
                UserInfo(content=reason, user=u).save()
                u.save()
            elif operation == '2':
                u = User.objects.get(id=int(uid))
                if u:
                    u.status = 2
                    u.save()
        return HttpResponseRedirect(reverse('user_mgr', kwargs={'page':page}))

def union_reg(request):
    if login_error(request):
        return HttpResponseRedirect(reverse('helo'))
    u = request.COOKIES.get('userid','').strip()
    u = User.objects.get(id=int(u))
    union = Union.objects.filter(owner=u).first()
    if request.method == 'GET':
        return render(request, 'union_reg.html', {'msg':'', 'union':union})
    else:
        uid = request.COOKIES.get('userid', '')
        msg = '申请成功，请耐心等待管理员审核！'
        name = request.POST.get('name', '').strip()
        content = request.POST.get('content', '').strip()

        f = request.FILES["myfile"]
        filename = f.name
        ext = filename[filename.index('.'):] if '.' in filename else '.jpg'
        filename = hashlib.md5(filename.encode()).hexdigest()
        if os.path.exists(filename+ext):
            filename = filename+'1'+ext
        else:
            filename = filename+ext

        with open(os.path.join('static','hws',filename), 'wb+') as dest:
            for chunk in f.chunks():
                dest.write(chunk)

        if uid and uid.isdigit() and name and content:
            un = Union.objects.filter(name=name)
            if not un:
                user = User.objects.get(id=int(uid))
                un = Union(name=name, content=content, owner=user, file_path=filename)
                un.save()
            else:
                msg = '盟团名称已被注册！'
        else:
            msg = '信息输入不全！'
        return render(request, 'union_reg.html', {'msg':msg, 'union':union})

def union_edit(request):
    if login_error(request):
        return HttpResponseRedirect(reverse('helo'))
    u = request.COOKIES.get('userid','').strip()
    u = User.objects.get(id=int(u))
    union = Union.objects.filter(owner=u).first()
    if request.method == 'GET':
        if union:
            return render(request, 'union_edit.html', {})
        else:
            return HttpResponseNotFound('Page is Lost.')
    else:
        content = request.POST.get('content', '').strip()
        if request.FILES["myfile"]:
            f = request.FILES["myfile"]
            filename = f.name
            ext = filename[filename.index('.'):] if '.' in filename else '.jpg'
            filename = hashlib.md5(filename.encode()).hexdigest()
            if os.path.exists(filename+ext):
                filename = filename+'1'+ext
            else:
                filename = filename+ext

            with open(os.path.join('static','hws',filename), 'wb+') as dest:
                for chunk in f.chunks():
                    dest.write(chunk)
        else:
            filename = None
        if content:
            union.content = content
        if filename:
            if union.file_path and os.path.exists(os.path.join('static','hws',union.file_path)):
                os.remove(os.path.join('static','hws',union.file_path))
            union.file_path = filename
        union.save()
        return HttpResponseRedirect(reverse('union_info'))


def union_mgr(request, page=1):
    if login_error(request, SUPER_PERM):
        return HttpResponseRedirect(reverse('helo'))
    if request.method == 'GET':
        unions = Union.objects.all()
        unions = Paginator(unions, PAGE_ITEMS)
        page_nums = get_page(page, unions.page_range)
        return render(request, 'union_mgr.html', {'unions':unions.page(page),'page': page, 'page_nums':page_nums, 'num_pages': unions.num_pages})
    elif request.method == 'POST':
        operation = request.POST.get('operation', '')
        uid = request.POST.get('id', '')
        if operation and uid and operation.isdigit() and uid.isdigit():
            if operation == '0':
                u = Union.objects.get(id=int(uid))
                if u:
                    u.status = 1
                    u.owner.permission = 1
                    u.owner.save()
                    u.save()
            elif operation == '1':
                u = Union.objects.get(id=int(uid))
                if u:
                    u.status = 2
                reason = request.POST.get('reason','')
                UnionInfo(content=reason, union=u).save()
                u.save()
            elif operation == '2':
                u = Union.objects.get(id=int(uid))
                if u:
                    u.status = 3
                    u.save()
        return HttpResponseRedirect(reverse('union_mgr', kwargs={'page':page}))


def union_owner_mgr(request):
    if login_error(request, UNION_PERM):
        return HttpResponseRedirect(reverse('helo'))
    return render(request, 'union_owner_mgr.html', {})

# edit
def union_info(request, union_id=None):
    if union_id:
        union = Union.objects.get(id=union_id)
        return render(request, 'union_info.html', {'union':union,'warning':None})
    uid = request.COOKIES.get('userid', '')
    if not uid or not uid.isdigit():
        return render(request, 'union_info.html', {'union':None,'warning':None})
    else:
        u = User.objects.get(id=int(uid))
        union = Union.objects.filter(owner=u).first()
        warning = UnionInfo.objects.filter(union=union).all().order_by('-create_date').first()
        if warning and (datetime.datetime.utcnow().replace(tzinfo=utc) - warning.create_date).days <= 5:
            warning = warning.content
        else:
            warning = None
        return render(request, 'union_info.html', {'union':union, 'warning':warning})


# 作品管理
def handwrt_mgr(request, page=1):
    if login_error(request, SUPER_UNION):
        return HttpResponseRedirect(reverse('helo'))
    utype = request.COOKIES.get('utype')
    if utype == '0':
        hws = HandWrite.objects.order_by('-score').all()
    else:
        u = request.COOKIES.get('userid','').strip()
        u = User.objects.get(id=int(u))
        union = Union.objects.get(owner=u)
        hws = HandWrite.objects.filter(in_union=union).order_by('-score')
    hws = Paginator(hws, PAGE_ITEMS)
    page_nums = get_page(page, hws.page_range)
    category_writes = CategoryWrite.objects.all()
    category_contents = CategoryContent.objects.all()
    if request.method == 'GET':
        return render(request, 'upload_handwrt.html', 
            {'hws':hws.page(page), 'category_writes':category_writes,
            'category_contents':category_contents, 'utype':utype,'page': page, 'page_nums':page_nums, 'num_pages':hws.num_pages})
    else:
        operation = request.POST.get('operation', '').strip()
        if operation == '2':
            u = request.COOKIES.get('userid','').strip()
            u = User.objects.get(id=int(u))
            category_write = request.POST.get('category_write')
            category_content = request.POST.get('category_content')
            title = request.POST.get('title','').strip()
            info = request.POST.get('info','').strip()
            description = request.POST.get('description','').strip()
            if title and category_write and category_content:
                category_write = CategoryWrite.objects.get(id=int(category_write))
                category_content = CategoryContent.objects.get(id=int(category_content))
                f = request.FILES["myfile"]
                filename = f.name
                ext = filename[filename.index('.'):] if '.' in filename else '.jpg'
                filename = hashlib.md5(filename.encode()).hexdigest()
                if os.path.exists(filename+ext):
                    filename = filename+'1'+ext
                else:
                    filename = filename+ext
                if utype == '1':
                    in_union = Union.objects.get(owner=u)
                    HandWrite(title=title, info=info, description=description, category_write=category_write,
                        category_content=category_content,file_path=filename, owner=u, in_union=in_union).save()
                else:
                    category_super = int(request.POST.get('category_super'))
                    HandWrite(title=title, info=info, description=description, category_write=category_write, flag=True,
                        category_content=category_content,file_path=filename, owner=u, 
                        category_super=category_super).save()

                with open(os.path.join('static','hws',filename), 'wb+') as dest:
                    for chunk in f.chunks():
                        dest.write(chunk)
        else:
            hid = request.POST.get('id','').strip()
            if hid and hid.isdigit():
                hw = HandWrite.objects.get(id=(int(hid)))
                if operation == '0':
                    hw.flag = True
                    hw.save()
                elif operation == '1':
                    # hw.flag = False
                    # hw.save()
                    hw.delete()
        # edit
        return render(request, 'upload_handwrt.html', 
            {'hws':hws.page(page), 'category_writes':category_writes,
            'category_contents':category_contents, 'utype':utype,'page': page, 'page_nums':page_nums, 'num_pages':hws.num_pages})


def get_handwrt_writes(request, unid=0, page=1):
    cid = request.GET.get('id').strip()
    get_params = '?id={}'.format(cid)
    category_write = CategoryWrite.objects.get(id=int(cid))
    hws = HandWrite.objects.filter(category_write=category_write)
    hws = Paginator(hws, PAGE_ITEMS)
    page_nums = get_page(page, hws.page_range)
    if unid:
        union = Union.objects.get(id=unid)
        hws = hws.filter(in_union=union).all()
    return render(request, 'displays.html', {'hws':hws.page(page), 'page': page, 'page_nums':page_nums,
        'page_name':'get_handwrt_writes', 'get_params':get_params, 'num_pages': hws.num_pages})
    
def display(request):
    hid = request.GET.get('id', '').strip()
    hw = HandWrite.objects.get(id=int(hid))
    info = request.COOKIES.get('info', '')
    hw.score += 1
    hw.save()
    comments = Comment.objects.filter(handwrite=hw)[:30]
    resp = render(request, 'display.html', {'hw':hw, 'info':info, 'comments':comments})
    if info:
        resp.set_cookie('info', '')
    return resp

def get_handwrt_contents(request, unid=0, page=1):
    # if not unid:
    #     return HttpResponseNotFound('<h1>Page not found</h1>')
    cid = request.GET.get('id').strip()
    get_params = '?id={}'.format(cid)
    category_content = CategoryContent.objects.get(id=int(cid))
    hws = HandWrite.objects.filter(category_content=category_content).all()
    if unid:
        union = Union.objects.get(id=unid)
        hws = hws.filter(in_union=union).all()
    hws = Paginator(hws, PAGE_ITEMS)
    page_nums = get_page(page, hws.page_range)
    return render(request, 'displays.html', {'hws':hws.page(page), 'page': page, 'page_nums':page_nums,
        'page_name':'get_handwrt_contents', 'get_params':get_params, 'num_pages':hws.num_pages})

def get_handwrts_union(request, unid=0, page=1):
    u = request.COOKIES.get('userid','').strip()
    if not unid:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    union = Union.objects.get(id=int(unid))
    if u:
        user = User.objects.get(id=u)
        if user in union.users.all() or union.owner == u:
            u = None
    hws = HandWrite.objects.filter(in_union=union).all()
    hws = Paginator(hws, PAGE_ITEMS)
    page_nums = get_page(page, hws.page_range)
    return render(request, 'union_displays.html', {'hws':hws.page(page), 'unid':unid, 'union':union, 'userid':u,
        'page': page, 'page_nums':page_nums, 'num_pages': hws.num_pages})

    
def get_handwrt_category_supers(request,page=1):
    cid = request.GET.get('id').strip()
    get_params = '?id={}'.format(cid)
    hws = HandWrite.objects.filter(category_super=int(cid)).all()
    hws = Paginator(hws, PAGE_ITEMS)
    page_nums = get_page(page, hws.page_range)
    return render(request, 'displays.html', {'hws':hws.page(page), 'page': page, 'page_nums':page_nums,
        'page_name':'get_handwrt_category_supers', 'get_params':get_params, 'num_pages': hws.num_pages})


def search(request, page=1):
    key = request.GET.get('key','').strip()
    get_params = '?key={}'.format(key)
    if key:
        hws = HandWrite.objects.filter(title__contains=key).all()[:10]
    else:
        hws = HandWrite.objects.all().order_by('-create_date')[:10]
    hws = Paginator(hws, PAGE_ITEMS)
    page_nums = get_page(page, hws.page_range)
    return render(request, 'displays.html', {'hws':hws.page(page), 'page': page, 'page_nums':page_nums,
        'page_name':'search', 'get_params':get_params, 'num_pages': hws.num_pages})

def personal(request):
    if login_error(request, [0,1,2]):
        return HttpResponseRedirect(reverse('helo'))
    if request.method == 'GET':
        return render(request, 'personal.html', {})

def user_info(request):
    uid = request.COOKIES.get('userid','').strip()
    info = request.GET.get('info', '')
    if uid and uid.isdigit():
        user = User.objects.get(id=int(uid))
        warnning_info = None
        if user.status == 1:
            warnning = UserInfo.objects.filter(user=user).order_by('-create_date').first()
            if warnning:
                warnning_info = warnning.content
        my_union = None
        if user.permission == 1:
            my_union = Union.objects.filter(owner=user).first()
        unions = user.members.all()
        return render(request, 'user_info.html', 
            {'user':user, 'warnning_info':warnning_info,
            'my_union':my_union, 'unions':unions, 'info':info})

def attend_union(request):
    u = request.COOKIES.get('userid','').strip()
    union_id = request.GET.get('union_id', '')
    if u and union_id and u.isdigit() and union_id.isdigit():
        u = User.objects.get(id=u)
        union = Union.objects.get(id=union_id)
        union.users.add(u)
        union.save()
        return JsonResponse({'status':0})
    return JsonResponse({'status':1})

# 作品管理
def person_handwrt_mgr(request, page=1):
    if login_error(request, ORDINARY_PERM):
        return HttpResponseRedirect(reverse('helo'))
    u = request.COOKIES.get('userid','').strip()
    u = User.objects.get(id=int(u))
    is_member = True if u.members.all() else False
    if is_member:
        unions = []
    else:
        unions = Union.objects.all()[:10]
    hws = HandWrite.objects.filter(owner=u)
    hws = Paginator(hws, PAGE_ITEMS)
    page_nums = get_page(page, hws.page_range)
    category_writes = CategoryWrite.objects.all()
    category_contents = CategoryContent.objects.all()
    utype = request.COOKIES.get('utype')
    if request.method == 'GET':
        return render(request, 'personal_handwrt.html', 
            {'hws':hws.page(page), 'category_writes':category_writes,
            'category_contents':category_contents, 'utype':utype,
            'page': page, 'page_nums':page_nums, 'is_member':is_member, 'unions':unions, 'num_pages':hws.num_pages})
    else:
        operation = request.POST.get('operation', '').strip()
        if operation == '2':
            category_write = request.POST.get('category_write')
            category_content = request.POST.get('category_content')
            title = request.POST.get('title','')
            info = request.POST.get('info','')
            if title and category_write and category_content:
                category_write = CategoryWrite.objects.get(id=int(category_write))
                category_content = CategoryContent.objects.get(id=int(category_content))
                f = request.FILES["myfile"]
                filename = f.name
                ext = filename[filename.index('.'):] if '.' in filename else '.jpg'
                filename = hashlib.md5(filename.encode()).hexdigest()
                if os.path.exists(filename+ext):
                    filename = filename+'1'+ext
                else:
                    filename = filename+ext
                # edit
                HandWrite(title=title, info=info, category_write=category_write,
                    category_content=category_content,file_path=filename, owner=u, in_union=u.members.all().first()).save()
                with open(os.path.join('static','hws',filename), 'wb+') as dest:
                    for chunk in f.chunks():
                        dest.write(chunk)
        else:
            hid = request.POST.get('id','').strip()
            if hid and hid.isdigit():
                hw = HandWrite.objects.get(id=(int(hid)))
                if operation == '1':
                    hw.delete()
        return render(request, 'personal_handwrt.html', 
            {'hws':hws.page(page), 'category_writes':category_writes,
            'category_contents':category_contents, 'utype':utype, 'is_member':is_member, 'unions':unions})

def page_test(request, page=1):
    print(page, type(page))
    print(reverse('page_test', kwargs={'page':1}))
    return render(request, 'page_test.html',{})

def edit_user(request):
    if login_error(request, ALL_PERM):
        return HttpResponseRedirect(reverse('helo'))
    info = request.GET.get('info', '')
    uid = request.COOKIES.get('userid','').strip()
    u = User.objects.get(id=int(uid))
    if request.method == 'GET':
        return render(request, 'edit_user.html', {'user':u, 'info': info})
    else:
        keys = ('opassword', 'password1', 'password2', 'email')
        params = {}
        for key in keys:
            params[key] = request.POST.get(key, '').strip()
        params = {k:v for k,v in params.items() if v}
        print(params)
        if len(params) == 4 or (len(params) == 3 and 'email' not in params):
            opassword = make_passwd(params['opassword'], u.name)
            if u.passwd == opassword and params['password1'] == params['password2']:
                u.passwd = make_passwd(params['password1'], u.name)
                u.email = email
                u.save()
                return HttpResponseRedirect(reverse(user_info) + '?info=个人信息修改成功！')
            else:
                return render(request, 'edit_user.html', {'user':u, 'info': '旧密码错误或新密码不匹配！'})
        else:
            return render(request, 'edit_user.html', {'user':u, 'info': '输入参数不完整！'})

# 点赞
def like(request):
    if request.method == 'POST':
        hid = request.POST.get('id', '')
        if hid and hid.isdigit():
            hw = HandWrite.objects.get(id=int(hid))
            hw.score += 1
            hw.save()
            return JsonResponse({'status':0})
    return JsonResponse({'status':1})

#评论
def comment(request):
    hid = request.POST.get('hwid', '').strip()
    if login_error(request, ALL_PERM):
        if hid:
            resp = HttpResponseRedirect(reverse('display')+'?id='+hid)
            resp.set_cookie('info', '请登录后评论！')
            return resp
        else:
            return HttpResponseRedirect(reverse('helo'))
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if hid and hid.isdigit():
            uid = request.COOKIES.get('userid','').strip()
            u = User.objects.get(id=int(uid))
            hw = HandWrite.objects.get(id=int(hid))
            Comment(content=content, handwrite=hw, user=u).save()
        return HttpResponseRedirect(reverse('display')+'?id='+hid)