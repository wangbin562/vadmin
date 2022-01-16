# !/usr/bin/python
# -*- coding=utf-8 -*-
from django.conf.urls import url
from vadmin_standard import views

urlpatterns = [
    url(r'^api', views.api_view),
]
