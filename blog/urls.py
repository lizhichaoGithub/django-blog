from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("",views.index,name="index"),
    path("index",views.index,name="index"),
    path("getvcode", views.getvcode, name="getvcode"),
    path("register",views.register,name="register"),
    path("login",views.login_view,name="login"),
    path("logout", views.logout_view, name="logout_view"),
    path("newarticle", views.newarticle, name="newarticle"),
    path("article", views.article, name="article"),
]