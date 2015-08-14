"""hackathon URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from .views import login_page, oauth2_callback, users_page, user_page, thankyou_page

urlpatterns = [
	url(r'^$', login_page),
	url(r'^oa2callback/$', oauth2_callback),
	url(r'^users/$', users_page, name="users"),
	url(r'^user/(?P<id>\d+)/$', user_page, name='user'),
	url(r'^thankyou/$', thankyou_page, name='thankyou'),
    url(r'^admin/', include(admin.site.urls)),
]
