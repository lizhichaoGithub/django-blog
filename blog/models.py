from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class User(AbstractUser):
    nickname = models.CharField(max_length=128, default='chaos')
    pass


class Article(models.Model):
    security = models.CharField(max_length=32, default='')
    title = models.CharField(max_length=256, default='')
    abs = models.CharField(max_length=256, default='')
    kws = models.CharField(max_length=128, default='')
    date = models.CharField(max_length=32, default='')
    userid = models.CharField(max_length=128, default='')
    username = models.CharField(max_length=128, default='')
    content = models.CharField(max_length=99999, default='')
    type = models.CharField(max_length=32, default='')
    good = models.IntegerField(default=0)
    viewcount = models.IntegerField(default=0)


class Comments(models.Model, object):
    article_id = models.IntegerField()
    commenter = models.CharField(max_length=128, default='')
    content = models.CharField(max_length=9999, default='')
    date = models.CharField(max_length=32, default='')
    good = models.IntegerField()

    def __repr__(self):
        return repr((self.id, self.article_id, self.commenter, self.content, self.address.date,self.good))


class UserProfile(models.Model):
    userid = models.IntegerField()

