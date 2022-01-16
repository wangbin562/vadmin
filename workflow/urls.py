# !/usr/bin/python
# -*- coding=utf-8 -*-

from django.conf.urls import url
from workflow import views

urlpatterns = [
    url(r'^workflow_view/$', views.workflow_view),
    url(r'^workflow_me_view/$', views.workflow_me_view),
    # url(r'^workflow_me_approve_view/$', views.workflow_me_approve_view),
    # url(r'^workflow_me_already_approve_view/$', views.workflow_me_already_approve_view),
    # url(r'^workflow_me_star_view/$', views.workflow_me_star_view),
    # url(r'^workflow_me_cc_view/$', views.workflow_me_cc_view),
    # url(r'^workflow_star_view/$', views.workflow_star_view),
    url(r'^workflow_approval_view/$', views.workflow_approval_view),
    url(r'^workflow_submit/$', views.workflow_submit),
    url(r'^workflow_save/$', views.workflow_save),
    url(r'^workflow_comment/$', views.workflow_comment),
    url(r'^workflow_cancel/$', views.workflow_cancel),
    url(r'^workflow_approval/$', views.workflow_approval),
    url(r'^workflow_turn_down/$', views.workflow_turn_down),
    url(r'^workflow_turn_down/$', views.workflow_turn_down),

]
