# !/usr/bin/python
# -*- coding=utf-8 -*-
import re
from django.core.cache import cache
from django.conf import settings


def get_cache(request):
    o_response = None
    if settings.V_CACHE:
        key = str(request)
        o_re = re.search("<WSGIRequest: .*'(.*)'>", key)
        key = o_re[1] if o_re else key
        o_response = cache.get(key[:250])

    return o_response


def set_cache(request, content):
    if settings.V_CACHE:
        key = str(request)
        o_re = re.search("<WSGIRequest: .*'(.*)'>", key)
        key = o_re[1] if o_re else key
        cache.set(key, content)
