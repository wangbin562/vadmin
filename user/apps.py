# !/usr/bin/python
# -*- coding=utf-8 -*-
# pylint: disable=C0111

from django.apps import AppConfig


class AppConfigEx(AppConfig):
    name = "user"
    verbose_name = u"用户"
