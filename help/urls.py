# !/usr/bin/python
# -*- coding=utf-8 -*-

from django.conf.urls import url
from help import views

urlpatterns = [
    # url(r'^v_change_list_help_menu/$', views.v_change_list_help_menu),
    url(r'^v_help_view/$', views.v_help_view),
]
