from sqlite3 import IntegrityError

from django.contrib.auth import authenticate, login, logout
from .models import User, Article
from . import db
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.core.mail import send_mail, send_mass_mail, EmailMultiAlternatives
from django.conf import settings
import random
import json, time

# Create your views here.
from django.urls import reverse


def article(req):
    if req.method == 'GET':
        aid = req.GET.get('aid')
        a = db.get_article_by_id(aid)
        print(a)
        return render(req, 'article.html', {'article': a})


def newarticle(req):
    if req.method == 'GET':
        return render(req, 'newarticle.html')

    else:
        title = req.POST.get('title')
        abs = req.POST.get('abs')
        kws = req.POST.get('keywords')
        content = req.POST.get('content')
        type = req.POST.get('type')
        date = time.strftime('%Y-%m-%d %H:%M')
        userid = req.user.id
        username = req.user.nickname
        security = req.POST.get('security')
        a = Article(username=username, title=title, abs=abs, kws=kws, content=content, type=type, date=date,
                    userid=userid, security=security)
        a.save()
        return redirect('/article?aid=' + str(a.id))


def logout_view(req):
    logout(req)
    return HttpResponseRedirect("index")


def index(req):
    a = db.get_articles_security('public')
    return render(req, 'index.html', {'articles': a})


def isuserexist(username):
    print(len(User.objects.all().filter(username=username)))
    return len(User.objects.all().filter(username=username)) > 0


def getvcode(req):
    if req.method == 'GET':
        email = req.GET.get('email')
        result = {}
        if not isuserexist(email):
            code = random.randint(1000, 9999)
            res = send_mail('混沌博客注册验证码',
                            '注册验证码为:' + str(code) + '，如果不是你本人操作，请忽略此邮件',
                            '1693922728@qq.com',
                            [email],
                            fail_silently=False)
            if res == 1:
                result = {'status': 'success'}
                req.session['vcode'] = str(code)
            else:
                result = {'status': 'fail'}
        else:
            result = {'status': 'fail', 'msg': 'userexisted'}

        return HttpResponse(json.dumps(result), content_type="application/json")


def register(req):
    if req.method == 'POST':
        vcode = req.POST.get('vcode')
        password = req.POST.get('password')
        email = req.POST.get('email')
        nickname = req.POST.get('nickname')
        password2 = req.POST.get('password2')
        if vcode == req.session.get('vcode'):
            try:
                user = User.objects.create_user(username=email, password=password, nickname=nickname)
                user.save()
            except IntegrityError:
                return HttpResponse()
            return render(req, 'middle.html', {'title': '注册成功', 'message': '注册账号成功，即将跳转到登录页面', 'target': '/login'})
        else:
            return render(req, 'regist.html', {'nickname': nickname,
                                               'email': email,
                                               'password': password,
                                               'password2': password2,
                                               'vcode_msg': '验证码错误'
                                               })

    else:
        return render(req, 'regist.html')


def set_login_code(req):
    a = random.randint(10,99)
    b = random.randint(10,99)
    code = str(a + b)
    req.session['code'] = code
    return str(a)+'+'+str(b)+'='


def login_view(req):
    if req.method == "POST":
        username = req.POST.get("username")
        password = req.POST.get("password")
        code = req.POST.get('code')
        if code != req.session.get('code'):
            return render(req, 'login.html', {'code_msg': '验证码错误','email':username,'password':password,'qcode':set_login_code(req)})

        if isuserexist(username):
            user = authenticate(req, username=username, password=password)
            if user is not None:
                login(req, user)
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(req, 'login.html', {'pwd_msg': '密码错误','email':username,'qcode':set_login_code(req)})
        else:
            return render(req, 'login.html', {'email_msg': '账户不存在','qcode':set_login_code(req)})
    else:
        return render(req, 'login.html' ,{'qcode':set_login_code(req)})
