# !/usr/bin/python
# -*- coding=utf-8 -*-

from django.conf.urls import url
from file_manager import views

urlpatterns = [
    url(r'^file_manager/(?P<opera_key>.*)/', views.file_manager_opera),

]
