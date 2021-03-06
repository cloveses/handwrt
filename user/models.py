from django.db import models
import datetime

# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=12, verbose_name='用户名')
    passwd = models.CharField(max_length=512, verbose_name='密码')
    email = models.EmailField(verbose_name='邮箱地址')
    permission = models.IntegerField(default=2, verbose_name='用户类型')
    status = models.IntegerField(default=0, verbose_name='用户状态')
    # 0 正常 1 警告 2 锁定

class UserInfo(models.Model):
    content = models.TextField()
    create_date = models.DateTimeField(default=datetime.datetime.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class HandWrite(models.Model):
    title = models.CharField(max_length=256, verbose_name='标题')
    info = models.TextField(verbose_name='作品简介')
    description = models.TextField(null=True, verbose_name='作品描述')
    category_write = models.ForeignKey('CategoryWrite', on_delete=models.CASCADE, verbose_name='书体分类')
    category_content = models.ForeignKey('CategoryContent', on_delete=models.CASCADE, verbose_name='内容分类')
    flag = models.BooleanField(default=False, verbose_name='审核情况')
    score = models.IntegerField(default=0, verbose_name='点赞数')
    file_path = models.CharField(max_length=256)
    create_date = models.DateTimeField(default=datetime.datetime.now)
    owner = models.ForeignKey('User', null=True, on_delete=models.CASCADE)
    category_super = models.IntegerField(null=True, default=0, verbose_name='管理员的分类')
    in_union = models.ForeignKey('Union', on_delete=models.CASCADE, null=True)

class Comment(models.Model):
    content = models.TextField(null=True, verbose_name='评论内容')
    create_date = models.DateTimeField(default=datetime.datetime.now)
    handwrite = models.ForeignKey('HandWrite', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)

class Union(models.Model):
    name = models.CharField(max_length=12, verbose_name='盟团名称')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner', verbose_name='管理者')
    cover = models.ForeignKey(HandWrite, null=True, on_delete=models.CASCADE, verbose_name='封面作品')
    status = models.IntegerField(default=0, verbose_name='审核状态')
    active = models.IntegerField(default=0, verbose_name='活跃度')
    create_date = models.DateTimeField(default=datetime.datetime.now)
    content = models.TextField()
    file_path = models.CharField(max_length=256)
    users = models.ManyToManyField(User, related_name='members')

class UnionInfo(models.Model):
    union = models.ForeignKey(Union, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField(default=datetime.datetime.now)

class CategoryWrite(models.Model):
    name = models.CharField(max_length=12, verbose_name='书体名称')

class CategoryContent(models.Model):
    name = models.CharField(max_length=12, verbose_name='内容类别')
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE)

class KnonWrite(models.Model):
    title = models.CharField(max_length=256, verbose_name='标题')
    info = models.TextField(verbose_name='作品简介')
    category_write = models.ForeignKey('CategoryWrite', on_delete=models.CASCADE, verbose_name='书体分类')
    category_content = models.ForeignKey('CategoryContent', on_delete=models.CASCADE, verbose_name='内容分类')
    score = models.IntegerField(default=0, verbose_name='点赞数')
