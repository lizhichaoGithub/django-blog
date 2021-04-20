from sqlite3 import IntegrityError

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User, Article
from . import db
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.core.mail import send_mail, send_mass_mail, EmailMultiAlternatives
from django.conf import settings
import random
import json, time
import markdown2

# Create your views here.
from django.urls import reverse


def resetpwd(req):
    if req.method == 'GET':
        return render(req, 'resetpwd.html')
    else:
        data = {}
        vcode = req.POST.get('vcode')
        if vcode != req.session.get('vcode'):
            data['vcode_msg'] = '验证码错误!'
            return render(req, 'resetpwd.html', data)
        else:
            pwd = req.POST.get('password')
            pwd2 = req.POST.get('password2')
            if pwd != pwd2:
                data['pwd2_msg'] = "密码不一致"
                return render(req, 'resetpwd.html', data)
            else:
                uname = req.POST.get('email')
                user = db.get_user_by_username(uname)
                try:
                    assert user is not None
                    user.set_password(pwd)
                    user.save()
                    return redirect('login')
                except:
                    data['email_msg'] = '操作失败'
                    return render(req, 'resetpwd.html', data)


@login_required
def changepwd(req):
    if req.method == 'POST':
        uname = req.POST.get('email')
        old_pwd = req.POST.get('oldpassword')
        new_pwd = req.POST.get('password')
        nickname = req.user.nickname
        user = authenticate(username=uname, password=old_pwd)
        try:
            assert user is not None
            if user is not None:
                user.set_password(new_pwd)
                user.save()
                logout(req)
                return redirect('/userzone?nickname=' + nickname)
        except:
            return render(req, 'middle.html', {
                'title': '密码修改失败',
                'message': '密码操作失败，即将跳转页面',
                'time': 3000,
                'target': 'userzone?nickname=' + nickname
            })


@login_required()
def userzone(req):
    if req.method == 'GET':
        uname = req.GET.get('nickname')
        u = db.get_user_by_nickname(uname)

        try:
            assert u is not None
            if u is not None:
                it = {}
                it['nickname'] = u.nickname
                it['email'] = u.username
                security = None
                if uname != req.user.nickname:
                    security = 'public'
                articles = db.get_articles_parms(security=security, user=uname)
                return render(req, 'person.html', {'it': it, "articles": articles})

        except:
            return redirect('index')


def getcomments(req):
    if req.method == 'POST':
        aid = req.POST.get('aid')
        cs = db.get_comments_by_aid(aid=aid)
        # delattr(c,'_state')
        res = []
        for c in cs:
            delattr(c, '_state')
            res.append(c)
        if cs is not None:
            return HttpResponse(json.dumps(res, default=lambda o: o.__dict__), content_type="application/json")


@login_required
def comment(req):
    if req.method == 'POST':
        content = req.POST.get('content')
        commenter = req.POST.get('commenter')
        aid = req.POST.get('aid')
        date = time.strftime('%Y-%m-%d %H:%M')
        good = 0
        c = db.new_comment(article_id=aid, content=content, commenter=commenter, date=date, good=good)
        delattr(c, '_state')
        if c is not None:
            return HttpResponse(json.dumps(c, default=lambda o: o.__dict__), content_type="application/json")


def article(req):
    if req.method == 'GET':
        aid = req.GET.get('aid')
        a = db.get_article_by_id(aid)
        a.content = markdown2.markdown(a.content)
        return render(req, 'article.html', {'article': a})


@login_required
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
        a = db.new_article(username=username, title=title, abs=abs, kws=kws, content=content, type=type, date=date,
                           userid=userid, security=security)
        return redirect('/article?aid=' + str(a.id))


def logout_view(req):
    logout(req)
    return HttpResponseRedirect("index")


def index(req):
    a = db.get_articles_parms('public', 'tech')
    b = db.get_articles_parms('public', 'life')
    print(b)
    return render(req, 'index.html', {'articles': a, 'lifes': b})


def isuserexist(username):
    return len(User.objects.all().filter(username=username)) > 0


def getvcode(req):
    if req.method == 'GET':
        email = req.GET.get('email')
        type = req.GET.get('t')
        if type == 'cz':
            if not isuserexist(email):
                return HttpResponse(json.dumps({'status': 'fail', 'msg': 'user_not_existed'}), content_type="application/json")
            code = random.randint(1000, 9999)
            res = send_mail('【混沌空间】验证码',
                            '密码重置验证码为:' + str(code) + '，如果不是你本人操作，请忽略此邮件',
                            '1693922728@qq.com',
                            [email],
                            fail_silently=False)
            if res == 1:
                result = {'status': 'success'}
                req.session['vcode'] = str(code)
            else:
                result = {'status': 'fail'}

        elif type == 'zc':
            result = {}
            if not isuserexist(email):
                code = random.randint(1000, 9999)
                res = send_mail('【混沌空间】注册验证码',
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
                result = {'status': 'fail', 'msg': 'user_existed'}

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
                req.session['vcode'] = None
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
    a = random.randint(10, 99)
    b = random.randint(10, 99)
    code = str(a + b)
    req.session['code'] = code
    return str(a) + '+' + str(b) + '='


def login_view(req):
    if req.method == "POST":
        username = req.POST.get("username")
        password = req.POST.get("password")
        code = req.POST.get('code')
        if code != req.session.get('code'):
            return render(req, 'login.html',
                          {'code_msg': '验证码错误', 'email': username, 'password': password, 'qcode': set_login_code(req)})

        if isuserexist(username):
            user = authenticate(req, username=username, password=password)
            if user is not None:
                login(req, user)
                next = req.GET.get("next")
                try:
                    return redirect(next)
                except:
                    return HttpResponseRedirect(reverse("index"))

            else:
                return render(req, 'login.html', {'pwd_msg': '密码错误', 'email': username, 'qcode': set_login_code(req)})
        else:
            return render(req, 'login.html', {'email_msg': '账户不存在,请先注册', 'qcode': set_login_code(req)})
    else:
        next = req.GET.get("next")
        return render(req, 'login.html', {'qcode': set_login_code(req), 'next': next})
