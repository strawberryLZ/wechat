"""untitled URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from api import views

urlpatterns = [
    url(r"^auction/", include("auction.urls", namespace='auction')),
    url(r'^admin/', admin.site.urls),
    url(r'login', views.login.as_view()),
    url(r'message', views.MessageView.as_view()),
    url(r'^upload$', views.DXmessageView.as_view()),
    url(r'^create$', views.model_create.as_view()),
    url(r'^article$', views.Article.as_view()),
    url(r'^articledetial$', views.Article_detial.as_view()),
    url(r'^comment$', views.Article_comment.as_view()),
    url(r'^title$', views.Huati.as_view()),
    url(r'^test_FB$', views.NewView.as_view()),
    url(r'^Vister$', views.VisterView.as_view()),
    # url(r'^create/task/$', au.create_task),
    # url(r'^get/result/$', au.get_result),

]
urlpatterns += [
    url(r"^webmaster/", include("webmaster.urls", namespace='webmaster')),
]
