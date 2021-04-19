from .models import Article


def get_article_by_id(aid):
    try:
        a = Article.objects.get(id=aid)
        return a
    except:
        return None


def get_articles_security(security):
    try:
        a = Article.objects.filter(security=security).order_by('-date')
        if len(a) > 0:
            return a
        return None
    except:
        return None
