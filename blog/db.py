from .models import Article,Comments,User

def get_user_by_nickname(uname):
    user = User.objects.filter(nickname=uname)
    try:
        return user[0]
    except:
        return None


def get_user_by_username(uname):
    user = User.objects.filter(username=uname)
    try:
        return user[0]
    except:
        return None



def get_article_by_id(aid):
    try:
        a = Article.objects.get(id=aid)
        return a
    except:
        return None


def new_comment( article_id,commenter,content ,date  ,good ):
    c = Comments(article_id=article_id, commenter=commenter,content=content,date=date, good=good)
    c.save()
    return Comments.objects.get(id=c.id)


def get_comments_by_aid(aid):
    try:
        cs = Comments.objects.filter(article_id=aid).order_by('-date')
        if len(cs)> 0:
            return cs
        else:
            return None
    except:
        return None



def new_article(username, title, abs, kws, content, type, date, userid, security):
    a = Article(username=username, title=title, abs=abs, kws=kws, content=content, type=type, date=date,
                userid=userid, security=security)
    a.save()

    return a


def get_articles_parms(security=None,type=None,user=None,kws=None):
    try:
        a = Article.objects.all()
        if security is not None:
            a = a.filter(security=security)
        if type is not None:
            a = a.filter(type=type)
        if user is not None:
            a = a.filter(username=user)
        if kws is not None:
            a = a.filter(kws=kws)

        #kws:TODO
        if len(a) > 0:
            return a
        return None
    except:
        return None



